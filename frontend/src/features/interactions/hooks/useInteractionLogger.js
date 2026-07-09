import { useEffect, useState } from "react";
import { initialFormState } from "../constants/formState";
import {
  deleteEntry,
  listEntries,
  loadEntry,
  mergeEntry,
  processMessage,
  saveEntry,
  saveNewEntry,
  updateEntry,
  getLogs,
} from "../services/interactionApi";
import { detectDuplicateEntry } from "../utils/duplicateDetection";

const ensureArray = (val) => {
  if (Array.isArray(val)) return val;
  if (!val) return [];
  if (typeof val === "string") {
    return val.split(",").map(s => s.trim()).filter(Boolean);
  }
  return [val];
};

const normalizeEntry = (entry) => {
  if (!entry) return entry;
  return {
    ...entry,
    attendees: ensureArray(entry.attendees),
    materialsShared: ensureArray(entry.materialsShared || entry.materials),
    samplesDistributed: ensureArray(entry.samplesDistributed),
    aiSuggestedFollowUps: ensureArray(entry.aiSuggestedFollowUps),
    voiceNoteSummary: !!entry.voiceNoteSummary,
  };
};

export const useInteractionLogger = () => {
  const [formData, setFormData] = useState(initialFormState);
  const [entries, setEntries] = useState([]);
  const [editingEntryId, setEditingEntryId] = useState(null);
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "Describe the interaction in plain language and I'll fill the log for you.",
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [duplicateState, setDuplicateState] = useState(null);

  const pushAssistantMessage = (content) => {
    setMessages((current) => [...current, { role: "assistant", content }]);
  };

  useEffect(() => {
    const loadSavedEntries = async () => {
      try {
        const responseData = await listEntries();
        setEntries((responseData.entries || []).map(normalizeEntry));
      } catch {
        pushAssistantMessage("I couldn't load saved interactions from the database.");
      }
    };

    loadSavedEntries();
  }, []);

  const handleFieldChange = (field, value) => {
    setFormData((current) => ({
      ...current,
      [field]: value,
    }));
  };

  const handleSendMessage = async (text) => {
    const trimmedText = text.trim();
    if (!trimmedText) {
      return;
    }

    setMessages((current) => [...current, { role: "user", content: trimmedText }]);
    setIsLoading(true);

    try {
      const responseData = await processMessage({
        userInput: trimmedText,
        currentState: formData,
      });

      if (responseData.form_data) {
        setFormData((current) => normalizeEntry({
          ...current,
          ...responseData.form_data,
        }));
      }

      pushAssistantMessage(
        responseData.message ||
          "Form updated from your message. You can keep refining anything on the left.",
      );
    } catch (error) {
      pushAssistantMessage(
        error.response?.data?.detail || "I couldn't process that message right now. Please try again.",
      );
    } finally {
      setIsLoading(false);
    }
  };

  const applyAgentSaveResponse = (responseData) => {
    if (responseData.entries) {
      setEntries(responseData.entries.map(normalizeEntry));
    }

    if (responseData.entry) {
      setFormData(normalizeEntry(responseData.entry));
    }

    if (responseData.message) {
      pushAssistantMessage(responseData.message);
    }
  };

  const handleSaveEntry = async () => {
    setIsSaving(true);

    try {
      if (editingEntryId) {
        const responseData = await updateEntry({
          entryId: editingEntryId,
          formData,
        });
        applyAgentSaveResponse(responseData);
        setEditingEntryId(null);
        return;
      }

      const localDuplicate = detectDuplicateEntry(formData, entries);
      if (localDuplicate) {
        setDuplicateState({
          ...localDuplicate,
          newEntry: { ...formData },
        });
        pushAssistantMessage(
          "Duplicate interaction detected. Do you want to merge it with the saved record or save it as new?",
        );
        return;
      }

      const responseData = await saveEntry({ formData });
      if (responseData.is_duplicate || responseData.status === "duplicate_detected") {
        setDuplicateState({
          ...(responseData.duplicate || {}),
          newEntry: { ...formData },
        });
        pushAssistantMessage(
          responseData.message || "Duplicate detected. Choose Merge or Save as New.",
        );
        return;
      }

      applyAgentSaveResponse(responseData);
    } catch (error) {
      pushAssistantMessage(
        error.response?.data?.detail || "I couldn't save the interaction right now.",
      );
    } finally {
      setIsSaving(false);
    }
  };

  const handleMergeDuplicate = async () => {
    if (!duplicateState?.matched_record?.id) {
      return;
    }

    setIsSaving(true);
    try {
      const responseData = await mergeEntry({
        matchedEntryId: duplicateState.matched_record.id,
        formData: duplicateState.newEntry,
      });
      setDuplicateState(null);
      applyAgentSaveResponse(responseData);
    } catch (error) {
      pushAssistantMessage(
        error.response?.data?.detail || "I couldn't merge the duplicate interaction right now.",
      );
    } finally {
      setIsSaving(false);
    }
  };

  const handleSaveAsNew = async () => {
    if (!duplicateState) {
      return;
    }

    setIsSaving(true);
    try {
      const responseData = await saveNewEntry({
        formData: duplicateState.newEntry,
      });
      setDuplicateState(null);
      applyAgentSaveResponse(responseData);
    } catch (error) {
      pushAssistantMessage(
        error.response?.data?.detail || "I couldn't save the interaction as a new record right now.",
      );
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancelDuplicate = () => {
    setDuplicateState(null);
    pushAssistantMessage("Duplicate save cancelled. You can keep editing before saving.");
  };

  const handleEditEntry = async (entryId) => {
    setIsLoading(true);
    try {
      const responseData = await loadEntry({ entryId });
      if (responseData.form_data) {
        setFormData(normalizeEntry(responseData.form_data));
      }
      setEditingEntryId(entryId);
      pushAssistantMessage(
        responseData.message || "Saved interaction loaded into the form for editing.",
      );
    } catch (error) {
      pushAssistantMessage(
        error.response?.data?.detail || "I couldn't load that saved interaction right now.",
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteEntry = async (entryId) => {
    setIsSaving(true);
    try {
      const responseData = await deleteEntry({ entryId });
      if (editingEntryId === entryId) {
        setEditingEntryId(null);
        setFormData(initialFormState);
      }
      applyAgentSaveResponse(responseData);
    } catch (error) {
      pushAssistantMessage(
        error.response?.data?.detail || "I couldn't delete that saved interaction right now.",
      );
    } finally {
      setIsSaving(false);
    }
  };

  const [logs, setLogs] = useState([]);
  const [isLogsLoading, setIsLogsLoading] = useState(false);

  const fetchLogs = async () => {
    setIsLogsLoading(true);
    try {
      const data = await getLogs();
      setLogs(data.logs || []);
    } catch (e) {
      console.error("Failed to load logs:", e);
    } finally {
      setIsLogsLoading(false);
    }
  };

  const handleResetForm = () => {
    setFormData(initialFormState);
    setEditingEntryId(null);
    pushAssistantMessage("The form is ready for a new interaction.");
  };

  return {
    formData,
    entries,
    editingEntryId,
    messages,
    isLoading,
    isSaving,
    duplicateState,
    logs,
    isLogsLoading,
    fetchLogs,
    handleFieldChange,
    handleSendMessage,
    handleSaveEntry,
    handleMergeDuplicate,
    handleSaveAsNew,
    handleCancelDuplicate,
    handleEditEntry,
    handleDeleteEntry,
    handleResetForm,
  };
};
