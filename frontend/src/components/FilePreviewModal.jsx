import { useEffect, useState } from "react";

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
    mimeType?.includes("json") ||
    [
      "txt",
      "md",
      "json",
      "geojson",
      "jsonl",
      "ljson",
      "ndjson",
      "xml",
      "log",
      "py",
      "js",
      "ts",
      "html",
      "htm",
      "css",
      "yaml",
      "yml",
      "svg",
    ].includes(ext)
  );
}

function isDocx(mimeType, ext) {
  return mimeType === "application/vnd.openxmlformats-officedocument.wordprocessingml.document" || ext === "docx";
}

function isSpreadsheet(mimeType, ext) {
  return (
    [
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      "application/vnd.ms-excel",
      "text/csv",
      "application/csv",
      "text/tab-separated-values",
    ].includes(mimeType) || ["xlsx", "xls", "csv", "tsv"].includes(ext)
  );
}

function isStructuredText(mimeType, ext) {
  return mimeType?.includes("json") || ["json", "geojson", "jsonl", "ljson", "ndjson"].includes(ext);
}

function formatStructuredText(text, ext) {
  const value = text.replace(/^\uFEFF/, "").trim();

  if (!value) {
    return "";
  }

  if (ext === "jsonl" || ext === "ndjson") {
    return value
      .split(/\r?\n/)
      .map((line) => {
        const trimmed = line.trim();

        if (!trimmed) {
          return "";
        }

        try {
          return JSON.stringify(JSON.parse(trimmed), null, 2);
        } catch {
          return line;
        }
      })
      .join("\n");
  }

  try {
    return JSON.stringify(JSON.parse(value), null, 2);
  } catch {
    return text;
  }
}

function TextPreview({ previewUrl, ext }) {
  const [content, setContent] = useState("");
  const [status, setStatus] = useState("loading");
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    const controller = new AbortController();

    async function loadContent() {
      setStatus("loading");
      setError("");
      setContent("");

      try {
        const response = await fetch(previewUrl, { signal: controller.signal });

        if (!response.ok) {
          throw new Error(`Falha ao carregar preview (${response.status})`);
        }

        const text = await response.text();

        if (!active) {
          return;
        }

        setContent(isStructuredText("", ext) ? formatStructuredText(text, ext) : text);
        setStatus("ready");
      } catch (fetchError) {
        if (!active || fetchError.name === "AbortError") {
          return;
        }

        setError("Nao foi possivel carregar o preview deste arquivo.");
        setStatus("error");
      }
    }

    loadContent();

    return () => {
      active = false;
      controller.abort();
    };
  }, [ext, previewUrl]);

  if (status === "loading") {
    return (
      <div className="preview-loading">
        <p className="muted">Carregando preview...</p>
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="preview-text-fallback">
        <p className="preview-fallback-note">{error}</p>
        <iframe title="Fallback preview" className="preview-fallback-frame" src={previewUrl} />
      </div>
    );
  }

  return (
    <div className="preview-text-shell">
      <pre className="preview-text" aria-label="Conteúdo do arquivo">
        {content || "Arquivo vazio."}
      </pre>
    </div>
  );
}

function DocxPreview({ previewUrl }) {
  const [html, setHtml] = useState("");
  const [status, setStatus] = useState("loading");

  useEffect(() => {
    let active = true;
    const controller = new AbortController();

    async function loadDocx() {
      setStatus("loading");
      setHtml("");

      try {
        const [response, mammothModule] = await Promise.all([
          fetch(previewUrl, { signal: controller.signal }),
          import("mammoth/mammoth.browser"),
        ]);

        if (!response.ok) {
          throw new Error(`Falha ao carregar preview (${response.status})`);
        }

        const arrayBuffer = await response.arrayBuffer();
        const mammoth = mammothModule.default || mammothModule;
        const result = await mammoth.convertToHtml({ arrayBuffer });

        if (!active) {
          return;
        }

        setHtml(result.value || "");
        setStatus("ready");
      } catch (error) {
        if (!active || error.name === "AbortError") {
          return;
        }

        setStatus("error");
      }
    }

    loadDocx();

    return () => {
      active = false;
      controller.abort();
    };
  }, [previewUrl]);

  if (status === "loading") {
    return (
      <div className="preview-loading">
        <p className="muted">Carregando documento...</p>
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="preview-text-fallback">
        <p className="preview-fallback-note">Nao foi possivel gerar preview do DOCX no navegador.</p>
        <iframe title="Fallback preview" className="preview-fallback-frame" src={previewUrl} />
      </div>
    );
  }

  return (
    <div className="preview-docx-shell">
      <article className="preview-docx" dangerouslySetInnerHTML={{ __html: html || "<p>Documento vazio.</p>" }} />
    </div>
  );
}

function SpreadsheetPreview({ previewUrl, ext }) {
  const [status, setStatus] = useState("loading");
  const [sheetName, setSheetName] = useState("");
  const [headers, setHeaders] = useState([]);
  const [rows, setRows] = useState([]);
  const [truncated, setTruncated] = useState(false);

  useEffect(() => {
    let active = true;
    const controller = new AbortController();

    async function loadSheet() {
      setStatus("loading");
      setSheetName("");
      setHeaders([]);
      setRows([]);
      setTruncated(false);

      try {
        const [response, xlsxModule] = await Promise.all([fetch(previewUrl, { signal: controller.signal }), import("xlsx")]);

        if (!response.ok) {
          throw new Error(`Falha ao carregar preview (${response.status})`);
        }

        const XLSX = xlsxModule.default || xlsxModule;
        const MAX_ROWS = 200;
        const MAX_COLS = 30;

        let workbook;
        if (ext === "csv" || ext === "tsv") {
          const raw = await response.text();
          const delimiter = ext === "tsv" ? "\t" : ",";
          workbook = XLSX.read(raw, { type: "string", FS: delimiter, raw: true, cellDates: true });
        } else {
          const arrayBuffer = await response.arrayBuffer();
          workbook = XLSX.read(arrayBuffer, { type: "array", raw: true, cellDates: true });
        }

        const firstSheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[firstSheetName];
        const matrix = XLSX.utils.sheet_to_json(worksheet, { header: 1, blankrows: false, defval: "" });

        if (!active) {
          return;
        }

        const limited = matrix.slice(0, MAX_ROWS).map((row) => row.slice(0, MAX_COLS));
        const widest = limited.reduce((max, row) => Math.max(max, row.length), 0);
        const normalized = limited.map((row) => {
          const clone = [...row];
          while (clone.length < widest) {
            clone.push("");
          }
          return clone;
        });

        const firstRow = normalized[0] || [];
        const hasHeaderLabels = firstRow.some((value) => String(value || "").trim() !== "");
        const safeHeaders = hasHeaderLabels
          ? firstRow.map((value, index) => String(value || `Coluna ${index + 1}`))
          : Array.from({ length: widest }, (_, index) => `Coluna ${index + 1}`);

        setSheetName(firstSheetName || "Planilha");
        setHeaders(safeHeaders);
        setRows(hasHeaderLabels ? normalized.slice(1) : normalized);
        setTruncated(matrix.length > MAX_ROWS || matrix.some((row) => row.length > MAX_COLS));
        setStatus("ready");
      } catch (error) {
        if (!active || error.name === "AbortError") {
          return;
        }

        setStatus("error");
      }
    }

    loadSheet();

    return () => {
      active = false;
      controller.abort();
    };
  }, [ext, previewUrl]);

  if (status === "loading") {
    return (
      <div className="preview-loading">
        <p className="muted">Carregando planilha...</p>
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="preview-text-fallback">
        <p className="preview-fallback-note">Nao foi possivel gerar preview da planilha.</p>
        <iframe title="Fallback preview" className="preview-fallback-frame" src={previewUrl} />
      </div>
    );
  }

  return (
    <div className="preview-sheet-shell">
      <div className="preview-sheet-head">
        <strong>{sheetName || "Planilha"}</strong>
        {truncated ? <span className="muted">Exibindo amostra (max 200 linhas x 30 colunas).</span> : null}
      </div>
      <div className="preview-sheet-grid">
        <table className="preview-sheet-table">
          <thead>
            <tr>
              {headers.map((header, index) => (
                <th key={`${header}-${index}`}>{header || `Coluna ${index + 1}`}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 ? (
              <tr>
                <td colSpan={Math.max(headers.length, 1)} className="preview-sheet-empty">
                  Sem dados para exibir.
                </td>
              </tr>
            ) : (
              rows.map((row, rowIndex) => (
                <tr key={`row-${rowIndex}`}>
                  {row.map((cell, colIndex) => (
                    <td key={`cell-${rowIndex}-${colIndex}`}>{String(cell ?? "")}</td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default function FilePreviewModal({ open, file, previewUrl, onClose, onDownload }) {
  if (!open || !file || !previewUrl) return null;

  const ext = getExtension(file.name);
  const mimeType = file.original_mime_type || file.mime_type || "";
  const showTextPreview = isTextLike(mimeType, ext);

  const renderPreview = () => {
    if (isImage(mimeType, ext)) {
      return <img className="preview-image" src={previewUrl} alt={file.name} />;
    }

    if (isPdf(mimeType, ext)) {
      return <iframe title={`Preview ${file.name}`} className="preview-frame" src={previewUrl} />;
    }

    if (isDocx(mimeType, ext)) {
      return <DocxPreview previewUrl={previewUrl} />;
    }

    if (isSpreadsheet(mimeType, ext)) {
      return <SpreadsheetPreview previewUrl={previewUrl} ext={ext} />;
    }

    if (showTextPreview) {
      return <TextPreview previewUrl={previewUrl} ext={ext} />;
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
