import { useEffect, useMemo, useState } from "react";
import { useDropzone } from "react-dropzone";
import { useSearchParams } from "react-router-dom";

import ConfirmModal from "../components/ConfirmModal";
import FolderBreadcrumbs from "../components/FolderBreadcrumbs";
import FilePreviewModal from "../components/FilePreviewModal";
import {
  createFileShareLink,
  deleteFile,
  downloadFile,
  hardDeleteFile,
  listTrashFiles,
  listFiles,
  requestDownloadUrl,
  restoreFile,
  uploadFileViaBackend,
} from "../api/files";
import { getApiErrorMessage } from "../api/client";
import useFolderNavigator from "../hooks/useFolderNavigator";

export default function FilesPage() {
  const [searchParams] = useSearchParams();
  const {
    currentFolderId,
    currentFolders,
    loadCurrentFolders,
    goToRoot,
    openFolder,
    path,
    goToPathIndex,
  } = useFolderNavigator();

  const [files, setFiles] = useState([]);
  const [trashFiles, setTrashFiles] = useState([]);
  const [status, setStatus] = useState("");
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [hardDeleteTarget, setHardDeleteTarget] = useState(null);
  const [restoreTarget, setRestoreTarget] = useState(null);
  const [confirmLoading, setConfirmLoading] = useState(false);
  const [activeView, setActiveView] = useState("active");
  const [previewFile, setPreviewFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState("");
  const [shareTarget, setShareTarget] = useState(null);
  const [sharePassword, setSharePassword] = useState("");
  const [shareExpiresInDays, setShareExpiresInDays] = useState("");
  const [shareLoading, setShareLoading] = useState(false);
  const [shareResult, setShareResult] = useState(null);
  const [uploadState, setUploadState] = useState({
    inProgress: false,
    filename: "",
    progress: 0,
  });

  const searchTerm = useMemo(() => {
    return (searchParams.get("search") || "").trim().toLowerCase();
  }, [searchParams]);

  const visibleFiles = useMemo(() => {
    if (!searchTerm) {
      return files;
    }

    return files.filter((file) => file.name.toLowerCase().includes(searchTerm));
  }, [files, searchTerm]);

  const loadCurrentFiles = async (folderId = currentFolderId) => {
    const data = await listFiles(folderId);
    setFiles(data);
    return data;
  };

  const loadTrashFiles = async () => {
    const data = await listTrashFiles();
    setTrashFiles(data);
    return data;
  };

  useEffect(() => {
    async function bootstrap() {
      await goToRoot();
      await loadCurrentFiles(null);
      await loadTrashFiles();
    }

    bootstrap().catch(() => setStatus("Erro ao carregar dados de arquivos."));
  }, [goToRoot]);

  const handleOpenFolder = async (folder) => {
    try {
      await openFolder(folder);
      await loadCurrentFiles(folder.id);
    } catch {
      setStatus("Nao foi possivel abrir a pasta.");
    }
  };

  const handleGoRoot = async () => {
    try {
      await goToRoot();
      await loadCurrentFiles(null);
    } catch {
      setStatus("Nao foi possivel voltar para a raiz.");
    }
  };

  const handleGoToIndex = async (index) => {
    try {
      const targetPath = path.slice(0, index + 1);
      const targetId = targetPath[targetPath.length - 1]?.id || null;
      await goToPathIndex(index);
      await loadCurrentFiles(targetId);
    } catch {
      setStatus("Nao foi possivel navegar no caminho.");
    }
  };

  const handleUploadFile = async (file) => {
    if (!file) return;

    try {
      setUploadState({ inProgress: true, filename: file.name, progress: 0 });
      setStatus("Enviando arquivo criptografado pelo servidor...");
      await uploadFileViaBackend(file, currentFolderId, (event) => {
        const total = event.total || file.size || 1;
        const percent = Math.min(100, Math.round((event.loaded * 100) / total));
        setUploadState((current) => ({ ...current, progress: percent }));
      });

      setStatus("Upload concluido com sucesso.");
      setUploadState({ inProgress: false, filename: "", progress: 100 });
      await loadCurrentFiles(currentFolderId);
      await loadCurrentFolders(currentFolderId);
    } catch (err) {
      setStatus(getApiErrorMessage(err, "Falha no upload."));
      setUploadState({ inProgress: false, filename: "", progress: 0 });
    } finally {
      setTimeout(() => {
        setUploadState((current) => {
          if (current.inProgress) {
            return current;
          }
          return { inProgress: false, filename: "", progress: 0 };
        });
      }, 900);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    multiple: false,
    disabled: uploadState.inProgress,
    onDrop: async (acceptedFiles) => {
      const file = acceptedFiles?.[0];
      await handleUploadFile(file);
    },
  });

  const handleManualFileInput = async (event) => {
    const file = event.target.files?.[0];
    await handleUploadFile(file);
    event.target.value = "";
  };

  const confirmDelete = async () => {
    if (!deleteTarget) return;

    setConfirmLoading(true);
    try {
      await deleteFile(deleteTarget.id);
      setDeleteTarget(null);
      setStatus("Arquivo movido para a lixeira.");
      await loadCurrentFiles(currentFolderId);
      await loadTrashFiles();
    } catch (err) {
      setStatus(getApiErrorMessage(err, "Nao foi possivel mover o arquivo para a lixeira."));
    } finally {
      setConfirmLoading(false);
    }
  };

  const confirmRestore = async () => {
    if (!restoreTarget) return;

    setConfirmLoading(true);
    try {
      await restoreFile(restoreTarget.id);
      setRestoreTarget(null);
      setStatus("Arquivo restaurado da lixeira.");
      await loadCurrentFiles(currentFolderId);
      await loadTrashFiles();
    } catch (err) {
      setStatus(getApiErrorMessage(err, "Nao foi possivel restaurar o arquivo."));
    } finally {
      setConfirmLoading(false);
    }
  };

  const confirmHardDelete = async () => {
    if (!hardDeleteTarget) return;

    setConfirmLoading(true);
    try {
      await hardDeleteFile(hardDeleteTarget.id);
      setHardDeleteTarget(null);
      setStatus("Arquivo excluido permanentemente.");
      await loadTrashFiles();
    } catch (err) {
      setStatus(getApiErrorMessage(err, "Nao foi possivel excluir permanentemente."));
    } finally {
      setConfirmLoading(false);
    }
  };

  const handleDownload = async (file) => {
    try {
      setStatus("Preparando download...");
      const { blob, filename } = await downloadFile(file.id);

      const objectUrl = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = objectUrl;
      anchor.download = filename || file.name;
      anchor.style.display = "none";
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(objectUrl);

      setStatus("Download iniciado.");
    } catch (err) {
      setStatus(getApiErrorMessage(err, "Nao foi possivel iniciar o download."));
    }
  };

  const handlePreview = async (file) => {
    try {
      setStatus("Preparando preview...");
      const { download_url } = await requestDownloadUrl(file.id);
      setPreviewFile(file);
      setPreviewUrl(download_url);
      setStatus("");
    } catch (err) {
      setStatus(getApiErrorMessage(err, "Nao foi possivel abrir o preview."));
    }
  };

  const closePreview = () => {
    setPreviewFile(null);
    setPreviewUrl("");
  };

  const openShareModal = (file) => {
    setShareTarget(file);
    setSharePassword("");
    setShareExpiresInDays("");
    setShareResult(null);
  };

  const closeShareModal = () => {
    if (shareLoading) return;
    setShareTarget(null);
    setSharePassword("");
    setShareExpiresInDays("");
    setShareResult(null);
  };

  const handleCreateShareLink = async () => {
    if (!shareTarget) return;

    try {
      setShareLoading(true);
      setStatus("");

      const daysValue = shareExpiresInDays.trim();
      const parsedDays = daysValue ? Number(daysValue) : null;
      if (daysValue && (!Number.isInteger(parsedDays) || parsedDays < 1 || parsedDays > 365)) {
        setStatus("Dias de expiracao deve ser um inteiro entre 1 e 365.");
        return;
      }

      const cleanPassword = sharePassword.trim();
      if (cleanPassword && cleanPassword.length < 4) {
        setStatus("Senha deve ter no minimo 4 caracteres.");
        return;
      }

      const result = await createFileShareLink(shareTarget.id, {
        expiresInDays: parsedDays,
        password: cleanPassword || null,
      });

      setShareResult(result);
      setStatus("Link publico gerado com sucesso.");
    } catch (err) {
      setStatus(getApiErrorMessage(err, "Nao foi possivel gerar o link publico."));
    } finally {
      setShareLoading(false);
    }
  };

  const copyShareLink = async () => {
    if (!shareResult?.public_url) return;

    try {
      await navigator.clipboard.writeText(shareResult.public_url);
      setStatus("Link copiado para a area de transferencia.");
    } catch {
      setStatus("Nao foi possivel copiar automaticamente. Copie manualmente.");
    }
  };

  return (
    <section className="page-block">
      <header className="page-header card">
        <h2>Gestao de Arquivos</h2>
        <FolderBreadcrumbs path={path} onGoRoot={handleGoRoot} onGoToIndex={handleGoToIndex} />
      </header>

      {status && <p className="status">{status}</p>}

      <section className="card action-card minimal">
        <div className="action-head">
          <h3>Upload de arquivo</h3>
        </div>
        <div className="upload-stack">
          <p className="muted">Criptografia no servidor ativada para todos os uploads.</p>
          <div
            {...getRootProps()}
            className={`dropzone ${isDragActive ? "drag-active" : ""} ${uploadState.inProgress ? "disabled" : ""}`}
          >
            <input {...getInputProps()} />
            <p className="dropzone-title">Arraste um arquivo aqui ou clique para selecionar</p>
            <p className="muted">
              {uploadState.inProgress
                ? `Enviando ${uploadState.filename}...`
                : "Upload via backend com criptografia obrigatoria no servidor."}
            </p>
          </div>
          {(uploadState.inProgress || uploadState.progress > 0) && (
            <div className="upload-progress-wrap" aria-live="polite">
              <div className="upload-progress-meta">
                <span>{uploadState.filename || "Arquivo"}</span>
                <strong>{uploadState.progress}%</strong>
              </div>
              <div className="upload-progress-track" role="progressbar" aria-valuemin={0} aria-valuemax={100} aria-valuenow={uploadState.progress}>
                <div className="upload-progress-fill" style={{ width: `${uploadState.progress}%` }} />
              </div>
            </div>
          )}
        </div>
      </section>

      <section className="card minimal view-switch">
        <div className="row-actions">
          <button
            className={activeView === "active" ? "primary" : "ghost"}
            onClick={() => setActiveView("active")}
          >
            Arquivos Ativos
          </button>
          <button
            className={activeView === "trash" ? "primary" : "ghost"}
            onClick={() => setActiveView("trash")}
          >
            Lixeira ({trashFiles.length})
          </button>
        </div>
      </section>

      {activeView === "active" ? (
      <section className="grid">
        <article className="card">
          <h3>Pastas</h3>
          <ul className="list">
            {currentFolders.length === 0 && <li>Nenhuma pasta neste nivel.</li>}
            {currentFolders.map((folder) => (
              <li key={folder.id}>
                <button className="link" onClick={() => handleOpenFolder(folder)}>
                  {folder.name}
                </button>
              </li>
            ))}
          </ul>
        </article>

        <article className="card">
          <h3>Arquivos</h3>
          <ul className="list">
            {visibleFiles.length === 0 && (
              <li>{searchTerm ? "Nenhum arquivo encontrado para a busca." : "Nenhum arquivo neste nivel."}</li>
            )}
            {visibleFiles.map((file) => (
              <li key={file.id}>
                <span>
                  {file.name} ({Math.ceil(file.size / 1024)} KB)
                </span>
                <div className="row-actions">
                  <button className="ghost" onClick={() => handlePreview(file)}>
                    Visualizar
                  </button>
                  <button className="ghost" onClick={() => handleDownload(file)}>
                    Baixar
                  </button>
                  <button className="ghost" onClick={() => openShareModal(file)}>
                    Compartilhar
                  </button>
                  <button className="danger" onClick={() => setDeleteTarget(file)}>
                    Excluir
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </article>
      </section>
      ) : (
      <section className="card">
        <h3>Lixeira</h3>
        <p className="muted">Arquivos removidos sao excluidos automaticamente apos 30 dias.</p>
        <ul className="list">
          {trashFiles.length === 0 && <li>Nenhum arquivo na lixeira.</li>}
          {trashFiles.map((file) => (
            <li key={file.id}>
              <span>
                {file.name} ({Math.ceil(file.size / 1024)} KB)
              </span>
              <div className="row-actions">
                <button className="ghost" onClick={() => setRestoreTarget(file)}>
                  Restaurar
                </button>
                <button className="danger" onClick={() => setHardDeleteTarget(file)}>
                  Excluir permanente
                </button>
              </div>
            </li>
          ))}
        </ul>
      </section>
      )}

      <ConfirmModal
        open={Boolean(deleteTarget)}
        title="Enviar para lixeira"
        description={`Deseja enviar o arquivo "${deleteTarget?.name || ""}" para a lixeira?`}
        confirmLabel="Mover para lixeira"
        loading={confirmLoading}
        onCancel={() => setDeleteTarget(null)}
        onConfirm={confirmDelete}
      />

      <ConfirmModal
        open={Boolean(restoreTarget)}
        title="Restaurar arquivo"
        description={`Deseja restaurar o arquivo "${restoreTarget?.name || ""}" da lixeira?`}
        confirmLabel="Restaurar"
        loading={confirmLoading}
        onCancel={() => setRestoreTarget(null)}
        onConfirm={confirmRestore}
      />

      <ConfirmModal
        open={Boolean(hardDeleteTarget)}
        title="Excluir permanentemente"
        description={`Deseja excluir permanentemente o arquivo "${hardDeleteTarget?.name || ""}"?`}
        confirmLabel="Excluir permanentemente"
        loading={confirmLoading}
        onCancel={() => setHardDeleteTarget(null)}
        onConfirm={confirmHardDelete}
      />

      <FilePreviewModal
        open={Boolean(previewFile && previewUrl)}
        file={previewFile}
        previewUrl={previewUrl}
        onClose={closePreview}
        onDownload={() => previewFile && handleDownload(previewFile)}
      />

      {shareTarget && (
        <div className="modal-overlay" role="presentation" onClick={closeShareModal}>
          <section
            className="modal card"
            role="dialog"
            aria-modal="true"
            aria-label="Criar link publico"
            onClick={(event) => event.stopPropagation()}
          >
            <h3>Compartilhar arquivo</h3>
            <p className="muted">Arquivo: {shareTarget.name}</p>

            <div className="form">
              <label>
                Expiracao em dias (opcional)
                <input
                  type="number"
                  min={1}
                  max={365}
                  value={shareExpiresInDays}
                  onChange={(event) => setShareExpiresInDays(event.target.value)}
                  placeholder="Ex: 7"
                  disabled={shareLoading}
                />
              </label>

              <label>
                Senha (opcional)
                <input
                  type="password"
                  value={sharePassword}
                  onChange={(event) => setSharePassword(event.target.value)}
                  placeholder="Mínimo 4 caracteres"
                  disabled={shareLoading}
                />
              </label>
            </div>

            {shareResult?.public_url && (
              <div className="share-link-result">
                <label>
                  Link publico
                  <input type="text" readOnly value={shareResult.public_url} />
                </label>
                <div className="row-actions">
                  <button className="ghost" onClick={copyShareLink}>
                    Copiar link
                  </button>
                </div>
              </div>
            )}

            <div className="modal-actions">
              <button className="ghost" onClick={closeShareModal} disabled={shareLoading}>
                Fechar
              </button>
              <button onClick={handleCreateShareLink} disabled={shareLoading}>
                {shareLoading ? "Gerando..." : "Gerar link"}
              </button>
            </div>
          </section>
        </div>
      )}
    </section>
  );
}
