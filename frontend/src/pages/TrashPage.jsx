import { useEffect, useState } from "react";
import { FaTrashArrowUp, FaTrashCan, FaClockRotateLeft } from "react-icons/fa6";

import ConfirmModal from "../components/ConfirmModal";
import { getApiErrorMessage } from "../api/client";
import { hardDeleteFile, listTrashFiles, restoreFile } from "../api/files";

function formatDate(value) {
  if (!value) return "Data indisponivel";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Data indisponivel";
  return date.toLocaleString("pt-BR");
}

export default function TrashPage() {
  const [files, setFiles] = useState([]);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(true);
  const [confirmLoading, setConfirmLoading] = useState(false);
  const [restoreTarget, setRestoreTarget] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);

  const loadTrash = async () => {
    const data = await listTrashFiles();
    setFiles(data);
  };

  useEffect(() => {
    async function bootstrap() {
      try {
        setLoading(true);
        await loadTrash();
      } catch {
        setStatus("Nao foi possivel carregar a lixeira.");
      } finally {
        setLoading(false);
      }
    }

    bootstrap();
  }, []);

  const handleRestore = async () => {
    if (!restoreTarget) return;

    setConfirmLoading(true);
    try {
      await restoreFile(restoreTarget.id);
      setStatus("Arquivo restaurado da lixeira.");
      setRestoreTarget(null);
      await loadTrash();
    } catch (err) {
      setStatus(getApiErrorMessage(err, "Nao foi possivel restaurar o arquivo."));
    } finally {
      setConfirmLoading(false);
    }
  };

  const handleHardDelete = async () => {
    if (!deleteTarget) return;

    setConfirmLoading(true);
    try {
      await hardDeleteFile(deleteTarget.id);
      setStatus("Arquivo excluido permanentemente.");
      setDeleteTarget(null);
      await loadTrash();
    } catch (err) {
      setStatus(getApiErrorMessage(err, "Nao foi possivel excluir permanentemente."));
    } finally {
      setConfirmLoading(false);
    }
  };

  return (
    <section className="page-block">
      <header className="page-header card">
        <p className="eyebrow">Gestao</p>
        <h2>Lixeira</h2>
        <p className="muted">Arquivos removidos permanecem disponiveis para restauracao antes da exclusao definitiva.</p>
      </header>

      {status && <p className="status">{status}</p>}

      <section className="card minimal">
        <div className="action-head">
          <h3>Itens na lixeira</h3>
          <span className="muted">{files.length} item(ns)</span>
        </div>

        {loading ? (
          <p className="muted">Carregando itens da lixeira...</p>
        ) : (
          <ul className="list">
            {files.length === 0 && <li>Nenhum arquivo na lixeira.</li>}
            {files.map((file) => (
              <li key={file.id}>
                <div className="file-item">
                  <div className="file-info">
                    <span className="file-name">
                      {file.name} ({Math.ceil(file.size / 1024)} KB)
                    </span>
                    <span className="muted">
                      Removido em: {formatDate(file.deleted_at)}
                    </span>
                  </div>
                </div>

                <div className="row-actions">
                  <button
                    className="ghost icon-only"
                    onClick={() => setRestoreTarget(file)}
                    title="Restaurar arquivo"
                    aria-label="Restaurar arquivo"
                  >
                    <FaTrashArrowUp aria-hidden="true" />
                  </button>
                  <button
                    className="danger icon-only"
                    onClick={() => setDeleteTarget(file)}
                    title="Excluir permanentemente"
                    aria-label="Excluir permanentemente"
                  >
                    <FaTrashCan aria-hidden="true" />
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}

        <p className="muted" style={{ marginTop: "1rem" }}>
          <FaClockRotateLeft aria-hidden="true" /> Itens excluidos sao removidos definitivamente ao fim do periodo de retencao.
        </p>
      </section>

      <ConfirmModal
        open={Boolean(restoreTarget)}
        title="Restaurar arquivo"
        description={`Deseja restaurar o arquivo "${restoreTarget?.name || ""}" da lixeira?`}
        confirmLabel="Restaurar"
        loading={confirmLoading}
        onCancel={() => setRestoreTarget(null)}
        onConfirm={handleRestore}
      />

      <ConfirmModal
        open={Boolean(deleteTarget)}
        title="Excluir permanentemente"
        description={`Deseja excluir permanentemente o arquivo "${deleteTarget?.name || ""}"?`}
        confirmLabel="Excluir permanentemente"
        loading={confirmLoading}
        onCancel={() => setDeleteTarget(null)}
        onConfirm={handleHardDelete}
      />
    </section>
  );
}