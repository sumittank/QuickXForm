function DuplicateModal({ duplicateState, isSaving, onMerge, onSaveAsNew, onCancel }) {
  if (!duplicateState) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/30 px-4">
      <div className="w-full max-w-md rounded-[18px] border border-amber-200 bg-white p-6 shadow-[0_20px_60px_rgba(15,23,42,0.18)]">
        <div className="inline-flex items-center rounded-full bg-amber-100 px-3 py-1 text-sm font-semibold text-amber-800">
          Duplicate detected
        </div>
        <h2 className="mt-4 text-xl font-semibold text-slate-800">
          Duplicate interaction detected ({duplicateState.confidence}% match)
        </h2>
        <p className="mt-2 text-sm leading-6 text-slate-600">{duplicateState.reason}</p>
        <p className="mt-3 text-sm leading-6 text-slate-500">
          Do you want to merge this interaction with the saved record, save it as a new record, or
          cancel?
        </p>

        <div className="mt-6 flex gap-3">
          <button
            type="button"
            onClick={onMerge}
            className="inline-flex flex-1 items-center justify-center rounded-[12px] bg-blue-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:opacity-60"
            disabled={isSaving}
          >
            Merge
          </button>
          <button
            type="button"
            onClick={onSaveAsNew}
            className="inline-flex flex-1 items-center justify-center rounded-[12px] border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:opacity-60"
            disabled={isSaving}
          >
            Save New
          </button>
          <button
            type="button"
            onClick={onCancel}
            className="inline-flex flex-1 items-center justify-center rounded-[12px] border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:opacity-60"
            disabled={isSaving}
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}

export default DuplicateModal;
