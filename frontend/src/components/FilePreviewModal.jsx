function getExtension(filename = "") {
  const parts = filename.toLowerCase().split(".");
  return parts.length > 1 ? parts.pop() : "";
}

function isImage(mimeType, ext) {
  return mimeType?.startsWith("image/") || ["png", "jpg", "jpeg", "gif", "webp", "bmp", "svg"].includes(ext);
}

function isPdf(mimeType, ext) {
  return mimeType === "application/pdf" || ext === "pdf";
}

function isVideo(mimeType, ext) {
  return mimeType?.startsWith("video/") || ["mp4", "webm", "ogg", "mov"].includes(ext);
}

function isAudio(mimeType, ext) {
  return mimeType?.startsWith("audio/") || ["mp3", "wav", "ogg", "m4a"].includes(ext);
}

function isTextLike(mimeType, ext) {
  return (
    mimeType?.startsWith("text/") ||
    ["txt", "md", "json", "csv", "xml", "log", "py", "js", "ts", "html", "css"].includes(ext)
  );
}

export default function FilePreviewModal({ open, file, previewUrl, onClose, onDownload }) {
  if (!open || !file || !previewUrl) return null;

  const ext = getExtension(file.name);
  const mimeType = file.mime_type || "";

  const renderPreview = () => {
    if (isImage(mimeType, ext)) {
      return <img className="preview-image" src={previewUrl} alt={file.name} />;
    }

    if (isPdf(mimeType, ext) || isTextLike(mimeType, ext)) {
      return <iframe title={`Preview ${file.name}`} className="preview-frame" src={previewUrl} />;
    }

    if (isVideo(mimeType, ext)) {
      return <video className="preview-video" src={previewUrl} controls preload="metadata" />;
    }

    if (isAudio(mimeType, ext)) {
      return <audio className="preview-audio" src={previewUrl} controls preload="metadata" />;
    }

    return (
      <div className="preview-empty">
        <p>Preview nao suportado para este tipo de arquivo.</p>
      </div>
    );
  };

  return (
    <div className="modal-overlay" role="presentation" onClick={onClose}>
      <section
        className="modal card preview-modal"
        role="dialog"
        aria-modal="true"
        aria-label="Preview de arquivo"
        onClick={(event) => event.stopPropagation()}
      >
        <header className="preview-header">
          <div>
            <h3>Preview</h3>
            <p className="muted">{file.name}</p>
          </div>
          <div className="row-actions">
            <button className="ghost" onClick={onDownload}>
              Baixar
            </button>
            <button className="ghost" onClick={onClose}>
              Fechar
            </button>
          </div>
        </header>

        <div className="preview-content">{renderPreview()}</div>
      </section>
    </div>
  );
}
