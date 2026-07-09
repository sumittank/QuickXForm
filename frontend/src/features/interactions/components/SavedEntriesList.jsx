function SavedEntriesList({ entries, editingEntryId, onEditEntry, onDeleteEntry }) {
  return (
    <section className="border-t border-slate-200 pt-8">
      <div className="mb-4 flex items-center justify-between gap-3">
        <h2 className="text-[15px] font-semibold text-slate-700">Saved Entries</h2>
        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
          {entries.length} total
        </span>
      </div>

      {entries.length === 0 ? (
        <div className="rounded-[12px] border border-dashed border-slate-200 bg-slate-50 px-4 py-6 text-sm text-slate-500">
          No interactions saved yet. Save this form to build a local history for duplicate
          detection.
        </div>
      ) : (
        <div className="space-y-3">
          {entries.map((entry) => (
            <div
              key={entry.id}
              className={`rounded-[12px] border px-4 py-4 ${
                editingEntryId === entry.id
                  ? "border-blue-200 bg-blue-50/70"
                  : "border-slate-200 bg-slate-50/80"
              }`}
            >
              <div className="flex flex-wrap items-center justify-between gap-2">
                <p className="text-sm font-semibold text-slate-800">
                  {entry.hcpName || "Unnamed interaction"}
                </p>
                <span className="text-xs font-medium text-slate-500">
                  {[entry.date, entry.time].filter(Boolean).join(" • ") || "No date/time"}
                </span>
              </div>

              <p className="mt-1 text-sm text-slate-600">
                {entry.topicsDiscussed || (Array.isArray(entry.materialsShared) ? entry.materialsShared.join(", ") : entry.materialsShared) || "No summary available."}
              </p>

              {Array.isArray(entry.attendees) && entry.attendees.length > 0 ? (
                <p className="mt-2 text-xs text-slate-500">Attendees: {entry.attendees.join(", ")}</p>
              ) : null}

              <div className="mt-4 flex gap-2">
                <button
                  type="button"
                  onClick={() => onEditEntry(entry.id)}
                  className="inline-flex items-center justify-center rounded-[10px] border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-700 transition hover:bg-slate-100"
                >
                  Edit
                </button>
                <button
                  type="button"
                  onClick={() => onDeleteEntry(entry.id)}
                  className="inline-flex items-center justify-center rounded-[10px] border border-rose-200 bg-white px-3 py-2 text-xs font-semibold text-rose-600 transition hover:bg-rose-50"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

export default SavedEntriesList;
