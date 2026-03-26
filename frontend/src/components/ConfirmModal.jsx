export default function ConfirmModal({
  open,
  title,
  description,
  confirmLabel = "Confirmar",
  cancelLabel = "Cancelar",
  onConfirm,
  onCancel,
  loading = false,
}) {
  if (!open) return null;

  return (
    <div className="modal-overlay" role="presentation" onClick={onCancel}>
      <section
        className="modal card"
        role="dialog"
        aria-modal="true"
        aria-label={title}
        onClick={(event) => event.stopPropagation()}
      >
        <h3>{title}</h3>
        <p>{description}</p>

        <div className="modal-actions">
          <button className="ghost" onClick={onCancel} disabled={loading}>
            {cancelLabel}
          </button>
          <button className="danger" onClick={onConfirm} disabled={loading}>
            {loading ? "Aguarde..." : confirmLabel}
          </button>
        </div>
      </section>
    </div>
  );
}
