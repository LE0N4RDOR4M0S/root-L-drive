import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";

import { getApiErrorMessage } from "../api/client";
import { downloadSharedFile, getSharedFileInfo } from "../api/files";

function formatDate(value) {
  if (!value) return "Sem expiração";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Sem expiração";
  return date.toLocaleString("pt-BR");
}

export default function PublicSharePage() {
  const { token } = useParams();
  const [info, setInfo] = useState(null);
  const [password, setPassword] = useState("");
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);

  const fileSizeKb = useMemo(() => {
    if (!info?.size) return 0;
    return Math.max(1, Math.ceil(info.size / 1024));
  }, [info]);

  useEffect(() => {
    async function loadInfo() {
      try {
        setLoading(true);
        const data = await getSharedFileInfo(token);
        setInfo(data);
        setStatus("");
      } catch (err) {
        setStatus(getApiErrorMessage(err, "Link indisponivel."));
      } finally {
        setLoading(false);
      }
    }

    if (token) {
      loadInfo();
    }
  }, [token]);

  const handleDownload = async () => {
    if (!token) return;

    try {
      setDownloading(true);
      setStatus("Preparando download...");
      const { blob, filename } = await downloadSharedFile(token, password || null);

      const objectUrl = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = objectUrl;
      anchor.download = filename || info?.filename || "arquivo";
      anchor.style.display = "none";
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(objectUrl);

      setStatus("Download iniciado.");
    } catch (err) {
      setStatus(getApiErrorMessage(err, "Falha ao baixar arquivo."));
    } finally {
      setDownloading(false);
    }
  };

  return (
    <main className="page login-page">
      <section className="card auth-card">
        <p className="eyebrow">Compartilhamento Público</p>
        <h2>Download de arquivo</h2>

        {loading ? (
          <p className="muted">Carregando informações do link...</p>
        ) : info ? (
          <div className="form">
            <p className="muted">
              <strong>{info.filename}</strong> ({fileSizeKb} KB)
            </p>
            <p className="muted">Expira em: {formatDate(info.expires_at)}</p>

            {info.requires_password && (
              <label>
                Senha do link
                <input
                  type="password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="Informe a senha"
                />
              </label>
            )}

            <button onClick={handleDownload} disabled={downloading}>
              {downloading ? "Baixando..." : "Baixar arquivo"}
            </button>
          </div>
        ) : null}

        {status && <p className="status">{status}</p>}
      </section>
    </main>
  );
}
