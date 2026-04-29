import { FaClock, FaCopy, FaKey, FaShieldHalved, FaSliders, FaSquarePlus } from "react-icons/fa6";

const apiKeys = [
  { name: "Dashboard Sync", scope: "files:read, folders:read", status: "Ativa", lastUsed: "há 2 min" },
  { name: "Agent Local", scope: "files:write, folders:write", status: "Expira em 12d", lastUsed: "hoje 09:12" },
  { name: "Analytics", scope: "files:read", status: "Revogada", lastUsed: "sem uso" },
];

const scopeChips = ["files:read", "files:write", "folders:read", "folders:write", "shares:create", "profile:read"];

export default function ApiKeysPage() {
  return (
    <section className="page-block">
      <header className="page-header card proto-hero">
        <div>
          <p className="eyebrow">Integrações</p>
          <h2>API Keys</h2>
          <p className="muted">
            Protótipo visual para geração e administração de chaves usadas por sistemas externos para consumir a API do projeto.
          </p>
        </div>
        <div className="proto-hero-badge">
          <FaShieldHalved aria-hidden="true" />
          <span>Chaves, escopos e revogação</span>
        </div>
      </header>

      <section className="proto-split">
        <article className="card proto-panel">
          <div className="action-head">
            <h3>Nova chave</h3>
            <span className="muted">geração simulada</span>
          </div>

          <div className="proto-form">
            <label className="proto-field">
              Nome da integração
              <div className="proto-input">Ex: automação RH</div>
            </label>

            <label className="proto-field">
              Expiração
              <div className="proto-row">
                <div className="proto-input compact">30 dias</div>
                <div className="proto-input compact">Renovação manual</div>
              </div>
            </label>

            <div className="proto-field">
              <span>Escopos</span>
              <div className="proto-chip-grid">
                {scopeChips.map((scope, index) => (
                  <span key={scope} className={`proto-chip ${index < 3 ? "active" : ""}`}>
                    {scope}
                  </span>
                ))}
              </div>
            </div>

            <div className="proto-secret-box">
              <div>
                <p className="eyebrow">Chave gerada</p>
                <code>pk_live_8b3f7c2d...a91e</code>
              </div>
              <button type="button" className="ghost icon-only" aria-label="Copiar chave">
                <FaCopy aria-hidden="true" />
              </button>
            </div>

            <div className="row-actions">
              <button type="button" className="primary">
                <FaSquarePlus aria-hidden="true" /> Gerar chave
              </button>
              <button type="button" className="ghost">
                Cancelar
              </button>
            </div>
          </div>
        </article>

        <article className="card proto-panel">
          <div className="action-head">
            <h3>Chaves existentes</h3>
            <span className="muted">3 registros</span>
          </div>

          <ul className="proto-key-list">
            {apiKeys.map((item) => (
              <li key={item.name} className="proto-key-item">
                <div className="proto-key-main">
                  <div className="proto-key-icon">
                    <FaKey aria-hidden="true" />
                  </div>
                  <div>
                    <strong>{item.name}</strong>
                    <p className="muted">{item.scope}</p>
                  </div>
                </div>

                <div className="proto-key-meta">
                  <span className={`status-pill ${item.status === "Ativa" ? "active" : item.status === "Revogada" ? "inactive" : ""}`}>
                    {item.status}
                  </span>
                  <span className="muted">
                    <FaClock aria-hidden="true" /> {item.lastUsed}
                  </span>
                </div>

                <div className="row-actions">
                  <button type="button" className="ghost icon-only" aria-label="Configurar escopos">
                    <FaSliders aria-hidden="true" />
                  </button>
                  <button type="button" className="ghost icon-only" aria-label="Copiar token">
                    <FaCopy aria-hidden="true" />
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </article>
      </section>
    </section>
  );
}