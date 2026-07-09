import AssistantChat from "../features/chat/components/AssistantChat";
import DuplicateModal from "../features/interactions/components/DuplicateModal";
import InteractionForm from "../features/interactions/components/InteractionForm";
import { useInteractionLogger } from "../features/interactions/hooks/useInteractionLogger";

function AppShell() {
  const {
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
  } = useInteractionLogger();

  return (
    <main className="min-h-screen bg-[#f3f4f6] px-4 py-5 md:px-6 xl:h-screen xl:overflow-hidden">
      <div className="mx-auto flex max-w-[1400px] flex-col gap-5 xl:h-[calc(100vh-2.5rem)] xl:flex-row xl:items-start">
        <section className="w-full overflow-hidden rounded-[18px] border border-slate-200 bg-white shadow-[0_10px_30px_rgba(15,23,42,0.08)] xl:h-full xl:w-[68%]">
          <InteractionForm
            formData={formData}
            onFieldChange={handleFieldChange}
            onSaveEntry={handleSaveEntry}
            onEditEntry={handleEditEntry}
            onDeleteEntry={handleDeleteEntry}
            onResetForm={handleResetForm}
            entries={entries}
            editingEntryId={editingEntryId}
            isSaving={isSaving}
            logs={logs}
            isLogsLoading={isLogsLoading}
            fetchLogs={fetchLogs}
          />
        </section>

        <section className="w-full overflow-hidden rounded-[18px] border border-slate-200 bg-white shadow-[0_10px_30px_rgba(15,23,42,0.08)] xl:h-full xl:w-[32%]">
          <AssistantChat
            messages={messages}
            isLoading={isLoading}
            onSendMessage={handleSendMessage}
          />
        </section>
      </div>

      <DuplicateModal
        duplicateState={duplicateState}
        isSaving={isSaving}
        onMerge={handleMergeDuplicate}
        onSaveAsNew={handleSaveAsNew}
        onCancel={handleCancelDuplicate}
      />
    </main>
  );
}

export default AppShell;
