import { useCallback, useEffect, useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";

import {
  deleteFile,
  listFiles,
  uploadFileViaBackend,
} from "../api/files";
import { createFolder, deleteFolder, listFolders } from "../api/folders";
import { clearAuth } from "../api/client";

export default function DashboardPage() {
  const navigate = useNavigate();
  const [folders, setFolders] = useState([]);
  const [files, setFiles] = useState([]);
  const [currentFolderId, setCurrentFolderId] = useState(null);
  const [newFolderName, setNewFolderName] = useState("");
  const [status, setStatus] = useState("");

  const currentFolder = useMemo(
    () => folders.find((folder) => folder.id === currentFolderId) || null,
    [folders, currentFolderId]
  );

  const loadData = async (folderId = currentFolderId) => {
    const [foldersData, filesData] = await Promise.all([
      listFolders(folderId),
      listFiles(folderId),
    ]);
    setFolders(foldersData);
    setFiles(filesData);
  };

  useEffect(() => {
    loadData(null).catch(() => setStatus("Falaha em carregar dashboard de dados"));
  }, []);

  const handleCreateFolder = async (event) => {
    event.preventDefault();
    if (!newFolderName.trim()) return;

    try {
      await createFolder(newFolderName.trim(), currentFolderId);
      setNewFolderName("");
      setStatus("Folder created");
      await loadData(currentFolderId);
    } catch (err) {
      setStatus(err?.response?.data?.detail || "Failed to create folder");
    }
  };

  const handleDeleteFolder = async (folderId) => {
    try {
      await deleteFolder(folderId);
      setStatus("Folder deleted");
      await loadData(currentFolderId);
    } catch (err) {
      setStatus(err?.response?.data?.detail || "Falha ao deletar pasta");
    }
  };

  const handleUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      setStatus("Uploading encrypted file via backend...");
      await uploadFileViaBackend(file, currentFolderId);

      setStatus("File uploaded successfully");
      await loadData(currentFolderId);
    } catch (err) {
      setStatus(err?.response?.data?.detail || "Upload failed");
    } finally {
      event.target.value = "";
    }
  };

  const handleDeleteFile = async (fileId) => {
    try {
      await deleteFile(fileId);
      setStatus("File deleted");
      await loadData(currentFolderId);
    } catch (err) {
      setStatus(err?.response?.data?.detail || "Failed to delete file");
    }
  };

  const handleLogout = () => {
    clearAuth();
    navigate("/login");
  };

  return (
    <main className="page dashboard-page">
      <header className="toolbar">
        <div>
          <h1>Root L Drive</h1>
          <p>{currentFolder ? `Folder: ${currentFolder.name}` : "Root folder"}</p>
        </div>
        <button onClick={handleLogout}>Logout</button>
      </header>

      {status && <p className="status">{status}</p>}

      <section className="card">
        <h2>Create Folder</h2>
        <form className="inline-form" onSubmit={handleCreateFolder}>
          <input
            value={newFolderName}
            onChange={(event) => setNewFolderName(event.target.value)}
            placeholder="Folder name"
            required
          />
          <button type="submit">Create</button>
        </form>
      </section>

      <section className="card">
        <h2>Upload File</h2>
        <input type="file" onChange={handleUpload} />
      </section>

      <section className="grid">
        <article className="card">
          <h2>Folders</h2>
          {currentFolderId && (
            <button className="ghost" onClick={() => setCurrentFolderId(null)}>
              Back to root
            </button>
          )}
          <ul className="list">
            {folders.length === 0 && <li>No folders found</li>}
            {folders.map((folder) => (
              <li key={folder.id}>
                <button className="link" onClick={() => setCurrentFolderId(folder.id)}>
                  {folder.name}
                </button>
                <button className="danger" onClick={() => handleDeleteFolder(folder.id)}>
                  Delete
                </button>
              </li>
            ))}
          </ul>
        </article>

        <article className="card">
          <h2>Files</h2>
          <ul className="list">
            {files.length === 0 && <li>No files found</li>}
            {files.map((file) => (
              <li key={file.id}>
                <span>
                  {file.name} ({Math.ceil(file.size / 1024)} KB)
                </span>
                <button className="danger" onClick={() => handleDeleteFile(file.id)}>
                  Delete
                </button>
              </li>
            ))}
          </ul>
        </article>
      </section>
    </main>
  );
}
