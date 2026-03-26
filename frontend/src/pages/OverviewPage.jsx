import { useEffect, useState } from "react";

import { listFiles } from "../api/files";
import { listFolders } from "../api/folders";

export default function OverviewPage() {
  const [stats, setStats] = useState({ folders: 0, files: 0 });
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadStats() {
      try {
        const [folders, files] = await Promise.all([listFolders(null), listFiles(null)]);
        setStats({ folders: folders.length, files: files.length });
      } catch {
        setError("Nao foi possivel carregar os indicadores.");
      }
    }

    loadStats();
  }, []);

  return (
    <section className="page-block">
      <header className="page-header card">
        <h2>Visao Geral</h2>
      </header>

      {error ? (
        <p className="error">{error}</p>
      ) : (
        <div className="stats-grid">
          <article className="card stat-card">
            <h3>Pastas na raiz</h3>
            <strong>{stats.folders}</strong>
            <p className="muted">Estruturas principais disponiveis para navegacao.</p>
          </article>
          <article className="card stat-card">
            <h3>Arquivos na raiz</h3>
            <strong>{stats.files}</strong>
            <p className="muted">Documentos imediatamente acessiveis na raiz.</p>
          </article>
          <article className="card stat-card emphasis">
            <h3>Governanca</h3>
            <strong>{stats.folders + stats.files}</strong>
            <p className="muted">Ativos mapeados no nivel principal do ambiente.</p>
          </article>
        </div>
      )}
    </section>
  );
}
