import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { FaRegCopy, FaLink, FaFileLines, FaCircleCheck, FaCircleXmark, FaRegClock } from "react-icons/fa6";

import { getApiErrorMessage } from "../api/client";
import { listSharedLinks } from "../api/sharedLinks";

function formatDate(value) {
  if (!value) return "Sem expiração";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Sem expiração";
  return date.toLocaleString("pt-BR");
}

function isExpired(item) {
  if (!item.expires_at) return false;
  const date = new Date(item.expires_at);
  return !Number.isNaN(date.getTime()) && date.getTime() <= Date.now();
}

export default function SharedLinksPage() {
  const navigate = useNavigate();
  const [items, setItems] = useState([]);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");
  const [query, setQuery] = useState("");

  const loadSharedLinks = async () => {
    const data = await listSharedLinks();
    setItems(data || []);
  };

  useEffect(() => {
    async function bootstrap() {
      try {
        setLoading(true);
        await loadSharedLinks();
      } catch (err) {
        setStatus(getApiErrorMessage(err, "Nao foi possivel carregar os links compartilhados."));
      } finally {
        setLoading(false);
      }
    }

    bootstrap();
  }, []);

  const visibleItems = useMemo(() => {
    const cleanQuery = query.trim().toLowerCase();
    return items.filter((item) => {
      const expired = isExpired(item);
      const statusMatch =
        filter === "all" ||
        (filter === "active" && !expired) ||
        (filter === "inactive" && expired);
      const textMatch =
        !cleanQuery ||
        item.file_name.toLowerCase().includes(cleanQuery) ||
        item.token.toLowerCase().includes(cleanQuery) ||
        item.file_id.toLowerCase().includes(cleanQuery);
      return statusMatch && textMatch;
    });
  }, [items, filter, query]);

  const activeCount = items.filter((item) => !isExpired(item)).length;
  const inactiveCount = items.length - activeCount;

  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      setStatus("Link copiado para a area de transferencia.");
    } catch {
      setStatus("Nao foi possivel copiar automaticamente.");
    }
  };

  return (
    <section className="page-block">
      <header className="page-header card">
        <p className="eyebrow">Ferramentas</p>
        <h2>Links Compartilhados</h2>
        <p className="muted">Veja todos os links ativos e inativos, com referencia direta ao arquivo de origem.</p>
      </header>

      {status && <p className="status">{status}</p>}

      <section className="stats-grid">
        <article className="card stat-card">
          <h3>Total</h3>
          <strong>{items.length}</strong>
          <p className="muted">Links cadastrados no ambiente.</p>
        </article>
        <article className="card stat-card">
          <h3>Ativos</h3>
          <strong>{activeCount}</strong>
          <p className="muted">Ainda podem ser abertos publicamente.</p>
        </article>
        <article className="card stat-card emphasis">
          <h3>Inativos</h3>
          <strong>{inactiveCount}</strong>
          <p className="muted">Expirados ou indisponiveis para uso publico.</p>
        </article>
      </section>

      <section className="card minimal">
        <div className="row-actions" style={{ justifyContent: "space-between", flexWrap: "wrap" }}>
          <input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Filtrar por nome do arquivo, token ou id"
            aria-label="Filtrar links compartilhados"
            style={{ minWidth: "260px", flex: "1 1 320px" }}
          />
          <div className="row-actions">
            <button type="button" className={filter === "all" ? "primary" : "ghost"} onClick={() => setFilter("all")}>
              Todos
            </button>
            <button type="button" className={filter === "active" ? "primary" : "ghost"} onClick={() => setFilter("active")}>
              Ativos
            </button>
            <button type="button" className={filter === "inactive" ? "primary" : "ghost"} onClick={() => setFilter("inactive")}>
              Inativos
            </button>
          </div>
        </div>
      </section>

      {loading ? (
        <section className="card">
          <p className="muted">Carregando links compartilhados...</p>
        </section>
      ) : (
        <section className="card">
          <div className="action-head">
            <h3>Lista de links</h3>
            <span className="muted">{visibleItems.length} resultado(s)</span>
          </div>

          <ul className="list shared-links-list">
            {visibleItems.length === 0 && <li>Nenhum link compartilhado encontrado.</li>}
            {visibleItems.map((item) => {
              const expired = isExpired(item);
              const openHref = item.public_url || `/share/${item.token}`;
              const referenceHref = item.folder_id
                ? `/files?folder_id=${encodeURIComponent(item.folder_id)}&folder_name=${encodeURIComponent(item.folder_name || "Pasta")}&file_id=${encodeURIComponent(item.file_id)}`
                : `/files?file_id=${encodeURIComponent(item.file_id)}`;

              return (
                <li key={item.id} className="shared-link-item">
                  <div className="file-item">
                    <div className="file-info">
                      <span className="file-name">{item.file_name}</span>
                      {item.folder_name && <span className="muted">Pasta: {item.folder_name}</span>}
                      <span className="muted">
                        <FaFileLines aria-hidden="true" /> ID do arquivo: {item.file_id}
                      </span>
                      <span className={`status-pill ${expired ? "inactive" : "active"}`}>
                        {expired ? <FaCircleXmark aria-hidden="true" /> : <FaCircleCheck aria-hidden="true" />}
                        {expired ? "Inativo" : "Ativo"}
                      </span>
                      <span className="muted">
                        <FaRegClock aria-hidden="true" /> Criado em {formatDate(item.created_at)}
                      </span>
                      <span className="muted">
                        Expira em {formatDate(item.expires_at)}
                      </span>
                      {item.has_password && <span className="status-pill">Com senha</span>}
                      {!item.file_exists && <span className="status-pill inactive">Arquivo removido</span>}
                    </div>
                  </div>

                  <div className="shared-link-actions">
                    <div className="shared-link-url">
                      <code>{openHref}</code>
                    </div>
                    <div className="row-actions">
                      <button type="button" className="ghost icon-only" onClick={() => copyToClipboard(openHref)} title="Copiar link">
                        <FaRegCopy aria-hidden="true" />
                      </button>
                      <button type="button" className="ghost icon-only" onClick={() => navigate(referenceHref)} title="Referenciar arquivo">
                        <FaLink aria-hidden="true" />
                      </button>
                      <button type="button" className="primary" onClick={() => window.open(openHref, "_blank", "noreferrer")}>Abrir público</button>
                    </div>
                  </div>
                </li>
              );
            })}
          </ul>
        </section>
      )}
    </section>
  );
}