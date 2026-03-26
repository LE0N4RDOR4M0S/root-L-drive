import { useEffect, useState } from "react";

import ConfirmModal from "../components/ConfirmModal";
import FolderBreadcrumbs from "../components/FolderBreadcrumbs";
import FolderTreeView from "../components/FolderTreeView";
import { createFolder, deleteFolder, listFolders } from "../api/folders";
import useFolderNavigator from "../hooks/useFolderNavigator";

async function buildFolderTree(parentId = null, path = []) {
  const folders = await listFolders(parentId);
  const nodes = [];

  for (const folder of folders) {
    const nextPath = [...path, folder];
    const children = await buildFolderTree(folder.id, nextPath);
    nodes.push({ folder, path: nextPath, children });
  }

  return nodes;
}

export default function FoldersPage() {
  const {
    currentFolderId,
    currentFolders,
    loadCurrentFolders,
    goToRoot,
    openFolder,
    goToFolderPath,
    path,
    goToPathIndex,
  } = useFolderNavigator();

  const [newFolderName, setNewFolderName] = useState("");
  const [status, setStatus] = useState("");
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [confirmLoading, setConfirmLoading] = useState(false);
  const [treeNodes, setTreeNodes] = useState([]);
  const [treeLoading, setTreeLoading] = useState(false);

  const loadTree = async () => {
    setTreeLoading(true);
    try {
      const nodes = await buildFolderTree(null, []);
      setTreeNodes(nodes);
    } finally {
      setTreeLoading(false);
    }
  };

  useEffect(() => {
    async function bootstrap() {
      await goToRoot();
      await loadTree();
    }

    bootstrap().catch(() => setStatus("Erro ao carregar pastas."));
  }, [goToRoot]);

  const handleCreateFolder = async (event) => {
    event.preventDefault();
    if (!newFolderName.trim()) return;

    try {
      await createFolder(newFolderName.trim(), currentFolderId);
      setNewFolderName("");
      setStatus("Pasta criada com sucesso.");
      await Promise.all([loadCurrentFolders(currentFolderId), loadTree()]);
    } catch (err) {
      setStatus(err?.response?.data?.detail || "Falha ao criar pasta.");
    }
  };

  const requestDelete = (folder) => {
    setDeleteTarget(folder);
  };

  const confirmDelete = async () => {
    if (!deleteTarget) return;

    setConfirmLoading(true);
    try {
      await deleteFolder(deleteTarget.id);
      setDeleteTarget(null);
      setStatus("Pasta removida.");
      await Promise.all([loadCurrentFolders(currentFolderId), loadTree()]);
    } catch (err) {
      setStatus(err?.response?.data?.detail || "Nao foi possivel remover a pasta.");
    } finally {
      setConfirmLoading(false);
    }
  };

  const handleTreeSelect = async (folderPath) => {
    try {
      await goToFolderPath(folderPath);
      setStatus("");
    } catch {
      setStatus("Nao foi possivel navegar pela arvore.");
    }
  };

  return (
    <section className="page-block">
      <header className="page-header card">
        <h2>Gestao de Pastas</h2>
        <FolderBreadcrumbs path={path} onGoRoot={goToRoot} onGoToIndex={goToPathIndex} />
      </header>

      {status && <p className="status">{status}</p>}

      <section className="card">
        <h3>Criar nova pasta</h3>
        <form className="inline-form" onSubmit={handleCreateFolder}>
          <input
            value={newFolderName}
            onChange={(event) => setNewFolderName(event.target.value)}
            placeholder="Nome da pasta"
            required
          />
          <button type="submit">Criar</button>
        </form>
      </section>

      <section className="grid folders-grid">
        <article className="card">
          <h3>Hierarquia das pastas</h3>
          {treeLoading ? (
            <p className="status">Carregando arvore...</p>
          ) : (
            <FolderTreeView
              nodes={treeNodes}
              selectedFolderId={currentFolderId}
              onSelect={handleTreeSelect}
            />
          )}
        </article>

        <article className="card">
          <h3>Pastas do nivel selecionado</h3>
          <ul className="list">
            {currentFolders.length === 0 && <li>Nenhuma pasta neste nivel.</li>}
            {currentFolders.map((folder) => (
              <li key={folder.id}>
                <button className="link" onClick={() => openFolder(folder)}>
                  {folder.name}
                </button>
                <button className="danger" onClick={() => requestDelete(folder)}>
                  Excluir
                </button>
              </li>
            ))}
          </ul>
        </article>
      </section>

      <ConfirmModal
        open={Boolean(deleteTarget)}
        title="Confirmar exclusao"
        description={`Deseja remover a pasta "${deleteTarget?.name || ""}"? Esta acao falhara se a pasta nao estiver vazia.`}
        confirmLabel="Excluir pasta"
        loading={confirmLoading}
        onCancel={() => setDeleteTarget(null)}
        onConfirm={confirmDelete}
      />
    </section>
  );
}
