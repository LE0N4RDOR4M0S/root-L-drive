import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";

import ConfirmModal from "../components/ConfirmModal";
import FolderBreadcrumbs from "../components/FolderBreadcrumbs";
import FilePreviewModal from "../components/FilePreviewModal";
import {
  completeUpload,
  deleteFile,
  downloadFile,
  listFiles,
  requestDownloadUrl,
  requestUploadUrl,
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
  const [status, setStatus] = useState("");
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [confirmLoading, setConfirmLoading] = useState(false);
  const [previewFile, setPreviewFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState("");

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

  useEffect(() => {
    async function bootstrap() {
      await goToRoot();
      await loadCurrentFiles(null);
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

  const handleUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      setStatus("Solicitando URL de upload...");
      const { upload_url, minio_key } = await requestUploadUrl(
        file.name,
        currentFolderId,
        file.type
      );

      setStatus("Enviando arquivo para storage...");
      await uploadToPresignedUrl(upload_url, file);

      setStatus("Registrando metadata...");
      await completeUpload({
        name: file.name,
        folderId: currentFolderId,
        minioKey: minio_key,
        size: file.size,
        mimeType: file.type || "application/octet-stream",
      });

      setStatus("Upload concluido com sucesso.");
      await loadCurrentFiles(currentFolderId);
      await loadCurrentFolders(currentFolderId);
    } catch (err) {
      setStatus(err?.response?.data?.detail || "Falha no upload.");
    } finally {
      event.target.value = "";
    }
  };

  const confirmDelete = async () => {
    if (!deleteTarget) return;

    setConfirmLoading(true);
    try {
      await deleteFile(deleteTarget.id);
      setDeleteTarget(null);
      setStatus("Arquivo removido.");
      await loadCurrentFiles(currentFolderId);
    } catch (err) {
      setStatus(err?.response?.data?.detail || "Nao foi possivel remover o arquivo.");
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
        <div className="upload-inline">
          <input className="file-input-minimal" type="file" onChange={handleUpload} />
        </div>
      </section>

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

      <ConfirmModal
        open={Boolean(deleteTarget)}
        title="Confirmar exclusao"
        description={`Deseja remover o arquivo "${deleteTarget?.name || ""}"?`}
        confirmLabel="Excluir arquivo"
        loading={confirmLoading}
        onCancel={() => setDeleteTarget(null)}
        onConfirm={confirmDelete}
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
