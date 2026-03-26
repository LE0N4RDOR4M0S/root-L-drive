import { useCallback, useMemo, useState } from "react";

import { listFolders } from "../api/folders";

export default function useFolderNavigator() {
  const [currentFolderId, setCurrentFolderId] = useState(null);
  const [path, setPath] = useState([]);
  const [currentFolders, setCurrentFolders] = useState([]);

  const loadCurrentFolders = useCallback(
    async (folderId = currentFolderId) => {
      const folders = await listFolders(folderId);
      setCurrentFolders(folders);
      return folders;
    },
    [currentFolderId]
  );

  const goToRoot = useCallback(async () => {
    setCurrentFolderId(null);
    setPath([]);
    const folders = await listFolders(null);
    setCurrentFolders(folders);
  }, []);

  const openFolder = useCallback(async (folder) => {
    setCurrentFolderId(folder.id);
    setPath((prev) => [...prev, folder]);
    const folders = await listFolders(folder.id);
    setCurrentFolders(folders);
  }, []);

  const goToFolderPath = useCallback(async (folderPath) => {
    const normalizedPath = Array.isArray(folderPath) ? folderPath : [];
    const targetFolder = normalizedPath[normalizedPath.length - 1] || null;
    const targetId = targetFolder?.id || null;

    setPath(normalizedPath);
    setCurrentFolderId(targetId);

    const folders = await listFolders(targetId);
    setCurrentFolders(folders);
  }, []);

  const goToPathIndex = useCallback(
    async (index) => {
      if (index < 0) {
        await goToRoot();
        return;
      }

      const nextPath = path.slice(0, index + 1);
      await goToFolderPath(nextPath);
    },
    [goToRoot, goToFolderPath, path]
  );

  const currentFolder = useMemo(() => {
    if (path.length === 0) return null;
    return path[path.length - 1];
  }, [path]);

  return {
    currentFolderId,
    currentFolder,
    path,
    currentFolders,
    setCurrentFolders,
    loadCurrentFolders,
    goToRoot,
    openFolder,
    goToFolderPath,
    goToPathIndex,
  };
}
