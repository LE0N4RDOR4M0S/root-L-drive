import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { FaStar } from "react-icons/fa6";

import { listFavorites, setFileFavorite, setFolderFavorite } from "../api/favorites";

export default function FavoritesPage() {
  const navigate = useNavigate();
  const [files, setFiles] = useState([]);
  const [folders, setFolders] = useState([]);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(true);

  const loadFavorites = async () => {
    const data = await listFavorites();
    setFiles(data.files || []);
    setFolders(data.folders || []);
  };

  useEffect(() => {
    async function bootstrap() {
      try {
        setLoading(true);
        await loadFavorites();
      } catch {
        setStatus("Nao foi possivel carregar os favoritos.");
      } finally {
        setLoading(false);
      }
    }

    bootstrap();
  }, []);

  const handleToggleFile = async (file) => {
    try {
      await setFileFavorite(file.id, false);
      await loadFavorites();
      setStatus("Arquivo removido dos favoritos.");
    } catch {
      setStatus("Nao foi possivel atualizar o arquivo favorito.");
    }
  };

  const handleToggleFolder = async (folder) => {
    try {
      await setFolderFavorite(folder.id, false);
      await loadFavorites();
      setStatus("Pasta removida dos favoritos.");
    } catch {
      setStatus("Nao foi possivel atualizar a pasta favorita.");
    }
  };

  return (
    <section className="page-block">
      <header className="page-header card">
        <h2>Favoritos</h2>
        <p className="muted">Arquivos e pastas marcados com estrela.</p>
      </header>

      {status && <p className="status">{status}</p>}

      {loading ? (
        <section className="card">
          <p className="muted">Carregando favoritos...</p>
        </section>
      ) : (
        <section className="grid folders-grid">
          <article className="card">
            <h3>Pastas favoritas</h3>
            <ul className="list">
              {folders.length === 0 && <li>Nenhuma pasta favoritada.</li>}
              {folders.map((folder) => (
                <li key={folder.id}>
                  <button className="link" onClick={() => navigate(`/folders?search=${encodeURIComponent(folder.name)}`)}>
                    {folder.name}
                  </button>
                  <div className="row-actions">
                    <button
                      className="ghost icon-only"
                      onClick={() => handleToggleFolder(folder)}
                      title="Remover dos favoritos"
                      aria-label="Remover pasta dos favoritos"
                    >
                      <FaStar aria-hidden="true" />
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          </article>

          <article className="card">
            <h3>Arquivos favoritos</h3>
            <ul className="list">
              {files.length === 0 && <li>Nenhum arquivo favoritado.</li>}
              {files.map((file) => (
                <li key={file.id}>
                  <button className="link" onClick={() => navigate(`/files?search=${encodeURIComponent(file.name)}`)}>
                    {file.name}
                  </button>
                  <div className="row-actions">
                    <button
                      className="ghost icon-only"
                      onClick={() => handleToggleFile(file)}
                      title="Remover dos favoritos"
                      aria-label="Remover arquivo dos favoritos"
                    >
                      <FaStar aria-hidden="true" />
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          </article>
        </section>
      )}
    </section>
  );
}