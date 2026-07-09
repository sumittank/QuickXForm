import { useState } from "react";
import FormField from "./FormField";
import SavedEntriesList from "./SavedEntriesList";

const interactionOptions = ["Meeting", "Call", "Email", "Virtual Meeting"];

const fieldClassName =
  "w-full rounded-[10px] border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-4 focus:ring-blue-100";

function InteractionForm({
  formData,
  onFieldChange,
  onSaveEntry,
  onEditEntry,
  onDeleteEntry,
  onResetForm,
  entries,
  editingEntryId,
  isSaving,
  logs = [],
  isLogsLoading = false,
  fetchLogs,
}) {
  const [showLogsModal, setShowLogsModal] = useState(false);

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between gap-4 border-b border-slate-200 px-5 py-5 md:px-6">
        <div>
          <h1 className="text-[22px] font-semibold tracking-tight text-slate-800">
            Log HCP Interaction
          </h1>
          {editingEntryId ? (
            <p className="mt-1 text-sm text-slate-500">Editing a saved interaction</p>
          ) : null}
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => {
              fetchLogs();
              setShowLogsModal(true);
            }}
            className="inline-flex items-center justify-center rounded-[12px] border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
          >
            View Logs
          </button>

          {editingEntryId ? (
            <button
              type="button"
              onClick={onResetForm}
              className="inline-flex items-center justify-center rounded-[12px] border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
            >
              New Entry
            </button>
          ) : null}

          <button
            type="button"
            onClick={onSaveEntry}
            className="inline-flex items-center justify-center rounded-[12px] bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
            disabled={isSaving}
          >
            {isSaving ? "Saving..." : editingEntryId ? "Update Entry" : "Save Entry"}
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-5 py-5 md:px-6">
        <div className="space-y-8">
          <section>
            <div className="mb-4">
              <h2 className="text-[15px] font-semibold text-slate-700">Interaction Details</h2>
            </div>

            <div className="grid gap-6 md:grid-cols-3">
              <FormField label="HCP Name">
                <input
                  className={fieldClassName}
                  type="text"
                  value={formData.hcpName || ""}
                  onChange={(event) => onFieldChange("hcpName", event.target.value)}
                  placeholder="Search or select HCP..."
                />
              </FormField>

              <FormField label="Interaction Type">
                <select
                  className={fieldClassName}
                  value={formData.interactionType || ""}
                  onChange={(event) => onFieldChange("interactionType", event.target.value)}
                >
                  <option value="">Select type</option>
                  {interactionOptions.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              </FormField>

              <FormField label="HCP Sentiment">
                <select
                  className={fieldClassName}
                  value={formData.hcpSentiment || ""}
                  onChange={(event) => onFieldChange("hcpSentiment", event.target.value)}
                >
                  <option value="">Select sentiment</option>
                  <option value="Positive">Positive</option>
                  <option value="Neutral">Neutral</option>
                  <option value="Negative">Negative</option>
                </select>
              </FormField>
            </div>
          </section>

          <section>
            <div className="grid gap-6 md:grid-cols-2">
              <FormField label="Date">
                <input
                  className={fieldClassName}
                  type="date"
                  value={formData.date || ""}
                  onChange={(event) => onFieldChange("date", event.target.value)}
                />
              </FormField>

              <FormField label="Time">
                <input
                  className={fieldClassName}
                  type="time"
                  value={formData.time || ""}
                  onChange={(event) => onFieldChange("time", event.target.value)}
                />
              </FormField>
            </div>
          </section>

          <section>
            <FormField label="Attendees">
              <input
                className={fieldClassName}
                type="text"
                value={Array.isArray(formData.attendees) ? formData.attendees.join(", ") : formData.attendees || ""}
                onChange={(event) => onFieldChange("attendees", event.target.value.split(","))}
                placeholder="Enter names or search..."
              />
            </FormField>
          </section>

          <section>
            <FormField label="Topics Discussed">
              <textarea
                className={`${fieldClassName} min-h-[112px] resize-none`}
                value={formData.topicsDiscussed || ""}
                onChange={(event) => onFieldChange("topicsDiscussed", event.target.value)}
                placeholder="Enter key discussion points..."
              />
            </FormField>

            <div className="mt-3 flex items-center gap-2">
              <input
                type="checkbox"
                id="voiceNoteSummary"
                checked={!!formData.voiceNoteSummary}
                onChange={(event) => onFieldChange("voiceNoteSummary", event.target.checked)}
                className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
              />
              <label htmlFor="voiceNoteSummary" className="text-sm font-medium text-slate-700 cursor-pointer select-none">
                Voice Note Summary (Consent Given)
              </label>
            </div>
          </section>

          <section className="pb-4">
            <div className="mb-2">
              <h2 className="text-[15px] font-semibold text-slate-700">
                Materials Shared / Samples Distributed
              </h2>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
              <div className="rounded-[12px] border border-slate-200 bg-slate-50/70 p-4">
                <p className="text-sm font-semibold text-slate-700">Materials Shared</p>
                <textarea
                  className={`${fieldClassName} mt-3 min-h-[120px] resize-none bg-white`}
                  value={Array.isArray(formData.materialsShared) ? formData.materialsShared.join(", ") : formData.materialsShared || ""}
                  onChange={(event) => onFieldChange("materialsShared", event.target.value.split(","))}
                  placeholder="No materials added."
                />
              </div>

              <div className="rounded-[12px] border border-slate-200 bg-slate-50/70 p-4">
                <p className="text-sm font-semibold text-slate-700">Samples Distributed</p>
                <textarea
                  className={`${fieldClassName} mt-3 min-h-[120px] resize-none bg-white`}
                  value={Array.isArray(formData.samplesDistributed) ? formData.samplesDistributed.join(", ") : formData.samplesDistributed || ""}
                  onChange={(event) => onFieldChange("samplesDistributed", event.target.value.split(","))}
                  placeholder="No samples distributed."
                />
              </div>
            </div>
          </section>

          <section>
            <div className="grid gap-6 md:grid-cols-2">
              <FormField label="Outcomes">
                <textarea
                  className={`${fieldClassName} min-h-[100px] resize-none`}
                  value={formData.outcomes || ""}
                  onChange={(event) => onFieldChange("outcomes", event.target.value)}
                  placeholder="Enter discussion outcomes..."
                />
              </FormField>

              <FormField label="Follow-Up Actions">
                <textarea
                  className={`${fieldClassName} min-h-[100px] resize-none`}
                  value={formData.followUpActions || ""}
                  onChange={(event) => onFieldChange("followUpActions", event.target.value)}
                  placeholder="Enter follow-up actions..."
                />
              </FormField>
            </div>
          </section>

          {Array.isArray(formData.aiSuggestedFollowUps) && formData.aiSuggestedFollowUps.length > 0 ? (
            <section className="rounded-[12px] border border-amber-100 bg-amber-50/50 p-4">
              <h3 className="text-sm font-semibold text-amber-800">AI Suggested Follow-Ups (Read-only)</h3>
              <ul className="mt-2 list-disc pl-5 text-sm text-slate-600 space-y-1">
                {formData.aiSuggestedFollowUps.map((action, index) => (
                  <li key={index}>{action}</li>
                ))}
              </ul>
            </section>
          ) : null}

          <SavedEntriesList
            entries={entries}
            editingEntryId={editingEntryId}
            onEditEntry={onEditEntry}
            onDeleteEntry={onDeleteEntry}
          />
        </div>
      </div>

      {showLogsModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-end bg-slate-900/40 backdrop-blur-sm">
          <div className="flex h-full w-full max-w-2xl flex-col bg-white p-6 shadow-2xl animate-in slide-in-from-right duration-200">
            <div className="flex items-center justify-between border-b border-slate-200 pb-4">
              <div>
                <h2 className="text-lg font-bold text-slate-800">Agent Execution Logs</h2>
                <p className="text-xs text-slate-500">Trace LangGraph node operations, LLM prompts, and DB transactions</p>
              </div>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={fetchLogs}
                  className="rounded-[8px] bg-slate-100 px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-200 transition"
                  disabled={isLogsLoading}
                >
                  {isLogsLoading ? "Refreshing..." : "Refresh"}
                </button>
                <button
                  type="button"
                  onClick={() => setShowLogsModal(false)}
                  className="rounded-[8px] border border-slate-200 px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition"
                >
                  Close
                </button>
              </div>
            </div>
            <div className="flex-1 overflow-y-auto py-4 space-y-4">
              {logs.length === 0 ? (
                <p className="text-sm text-slate-500 text-center py-8">No logs captured yet.</p>
              ) : (
                logs.map((log, index) => (
                  <div key={index} className="rounded-[12px] border border-slate-200 bg-slate-50/50 p-4 text-xs font-mono space-y-2">
                    <div className="flex justify-between text-[10px] font-semibold text-slate-400">
                      <span>{log.timestamp ? new Date(log.timestamp).toLocaleString() : "Just now"}</span>
                      <span className="uppercase tracking-wider px-1.5 py-0.5 rounded bg-slate-200 text-slate-600">{log.action}</span>
                    </div>
                    {log.user_input && (
                      <div>
                        <span className="font-semibold text-blue-600">User Input:</span> "{log.user_input}"
                      </div>
                    )}
                    {log.tool_name && (
                      <div className="pt-1 border-t border-slate-100">
                        <span className="font-semibold text-amber-600">Tool Triggered:</span> <span className="font-bold text-slate-700">{log.tool_name}</span>
                        {log.tool_input && (
                          <pre className="mt-1 max-h-32 overflow-y-auto rounded bg-slate-100 p-2 text-[10px] text-slate-600 whitespace-pre-wrap">
                            {JSON.stringify(log.tool_input, null, 2)}
                          </pre>
                        )}
                        {log.tool_output && (
                          <pre className="mt-1 max-h-48 overflow-y-auto rounded bg-slate-900 text-cyan-400 p-2 text-[10px] whitespace-pre-wrap">
                            {JSON.stringify(log.tool_output, null, 2)}
                          </pre>
                        )}
                      </div>
                    )}
                    {log.final_response && (
                      <div className="pt-1 border-t border-slate-100">
                        <span className="font-semibold text-emerald-600">Final Response:</span>
                        <pre className="mt-1 max-h-48 overflow-y-auto rounded bg-emerald-50 text-slate-700 p-2 text-[10px] whitespace-pre-wrap">
                          {JSON.stringify(log.final_response, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default InteractionForm;
