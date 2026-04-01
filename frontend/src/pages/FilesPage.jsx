import { useEffect, useMemo, useState } from "react";
import { useDropzone } from "react-dropzone";
import { useSearchParams } from "react-router-dom";

import ConfirmModal from "../components/ConfirmModal";
import FolderBreadcrumbs from "../components/FolderBreadcrumbs";
import FilePreviewModal from "../components/FilePreviewModal";
import {
  completeUpload,
  deleteFile,
  downloadFile,
  hardDeleteFile,
  listTrashFiles,
  listFiles,
  requestDownloadUrl,
  requestUploadUrl,
  restoreFile,
  uploadToPresignedUrl,
} from "../api/files";
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
      setStatus("Solicitando URL de upload...");
      const { upload_url, minio_key } = await requestUploadUrl(
        file.name,
        currentFolderId,
        file.type
      );

      setStatus("Enviando arquivo para storage...");
      await uploadToPresignedUrl(upload_url, file, (event) => {
        const total = event.total || file.size || 1;
        const percent = Math.min(100, Math.round((event.loaded * 100) / total));
        setUploadState((current) => ({ ...current, progress: percent }));
      });

      setStatus("Registrando metadata...");
      await completeUpload({
        name: file.name,
        folderId: currentFolderId,
        minioKey: minio_key,
        size: file.size,
        mimeType: file.type || "application/octet-stream",
      });

      setStatus("Upload concluido com sucesso.");
      setUploadState({ inProgress: false, filename: "", progress: 100 });
      await loadCurrentFiles(currentFolderId);
      await loadCurrentFolders(currentFolderId);
    } catch (err) {
      setStatus(err?.response?.data?.detail || "Falha no upload.");
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
      setStatus(err?.response?.data?.detail || "Nao foi possivel mover o arquivo para a lixeira.");
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
      setStatus(err?.response?.data?.detail || "Nao foi possivel restaurar o arquivo.");
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
      setStatus(err?.response?.data?.detail || "Nao foi possivel excluir permanentemente.");
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
      setStatus(err?.response?.data?.detail || "Nao foi possivel iniciar o download.");
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
      setStatus(err?.response?.data?.detail || "Nao foi possivel abrir o preview.");
    }
  };

  const closePreview = () => {
    setPreviewFile(null);
    setPreviewUrl("");
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
          <div
            {...getRootProps()}
            className={`dropzone ${isDragActive ? "drag-active" : ""} ${uploadState.inProgress ? "disabled" : ""}`}
          >
            <input {...getInputProps()} />
            <p className="dropzone-title">Arraste um arquivo aqui ou clique para selecionar</p>
            <p className="muted">
              {uploadState.inProgress
                ? `Enviando ${uploadState.filename}...`
                : "Upload direto para o storage com URL assinada."}
            </p>
          </div>
          <div className="upload-inline">
            <input className="file-input-minimal" type="file" onChange={handleManualFileInput} />
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
    </section>
  );
}
