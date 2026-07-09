import axios from "axios";
import { API_BASE_URL } from "../../../config/api";

const invokeAgent = async (payload) => {
  const response = await axios.post(`${API_BASE_URL}/agent/invoke`, payload);
  return response.data;
};

export const listEntries = () =>
  invokeAgent({
    action: "list_entries",
  });

export const processMessage = ({ userInput, currentState }) =>
  invokeAgent({
    action: "process_message",
    user_input: userInput,
    current_state: currentState,
  });

export const updateEntry = ({ entryId, formData }) =>
  invokeAgent({
    action: "update_entry",
    entry_id: entryId,
    form_data: formData,
  });

export const saveEntry = ({ formData }) =>
  invokeAgent({
    action: "save_entry",
    form_data: formData,
  });

export const mergeEntry = ({ matchedEntryId, formData }) =>
  invokeAgent({
    action: "merge_entry",
    matched_entry_id: matchedEntryId,
    form_data: formData,
  });

export const saveNewEntry = ({ formData }) =>
  invokeAgent({
    action: "save_new_entry",
    form_data: formData,
  });

export const loadEntry = ({ entryId }) =>
  invokeAgent({
    action: "load_entry",
    entry_id: entryId,
  });

export const deleteEntry = ({ entryId }) =>
  invokeAgent({
    action: "delete_entry",
    entry_id: entryId,
  });

export const getLogs = async () => {
  const response = await axios.get(`${API_BASE_URL}/agent/logs`);
  return response.data;
};
