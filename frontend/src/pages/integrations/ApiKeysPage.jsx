import { useEffect, useMemo, useState } from "react";
import { FaClock, FaCopy, FaKey, FaShieldHalved, FaSliders, FaSquarePlus, FaCircleInfo } from "react-icons/fa6";

import ConfirmModal from "../../components/ConfirmModal";
import ApiKeyDocsModal from "../../components/ApiKeyDocsModal";
import { createApiKey, listApiKeys, revokeApiKey } from "../../api/apiKeys";

const scopeOptions = [
  "files:read",
  "files:write",
  "folders:read",
  "folders:write",
  "shares:create",
  "profile:read",
  "notifications:read",
];

function formatDate(value) {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "-";
  return date.toLocaleString("pt-BR");
}

export default function ApiKeysPage() {
  const [apiKeys, setApiKeys] = useState([]);
  const [name, setName] = useState("");
  const [selectedScopes, setSelectedScopes] = useState(["files:read"]);
  const [expiresInDays, setExpiresInDays] = useState("");
  const [generatedKey, setGeneratedKey] = useState("");
  const [generatedLabel, setGeneratedLabel] = useState("");
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [revokeTarget, setRevokeTarget] = useState(null);
  const [revokeLoading, setRevokeLoading] = useState(false);
  const [docsOpen, setDocsOpen] = useState(false);

  const activeCount = useMemo(() => apiKeys.filter((item) => item.is_active).length, [apiKeys]);
  const revokedCount = apiKeys.length - activeCount;

  const loadApiKeys = async () => {
    const data = await listApiKeys();
    setApiKeys(data || []);
  };

  useEffect(() => {
    async function bootstrap() {
      try {
        setLoading(true);
        await loadApiKeys();
      } catch {
        setStatus("Nao foi possivel carregar as API Keys.");
      } finally {
        setLoading(false);
      }
    }

    bootstrap();
  }, []);

  const toggleScope = (scope) => {
    setSelectedScopes((current) =>
      current.includes(scope) ? current.filter((item) => item !== scope) : [...current, scope]
    );
  };

  const handleCreate = async (event) => {
    event.preventDefault();
    if (!name.trim()) {
      setStatus("Informe um nome para a chave.");
      return;
    }

    try {
      setSubmitting(true);
      const result = await createApiKey({
        name: name.trim(),
        scopes: selectedScopes,
        expiresInDays: expiresInDays.trim() ? Number(expiresInDays) : null,
      });
      setGeneratedKey(result.api_key);
      setGeneratedLabel(result.name);
      setName("");
      setSelectedScopes(["files:read"]);
      setExpiresInDays("");
      setStatus("API Key criada com sucesso. Copie o valor exibido agora.");
      await loadApiKeys();
    } catch (error) {
      setStatus(error?.response?.data?.detail || "Nao foi possivel criar a API Key.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleCopyGeneratedKey = async () => {
    if (!generatedKey) return;

    try {
      await navigator.clipboard.writeText(generatedKey);
      setStatus("API Key copiada para a area de transferencia.");
    } catch {
      setStatus("Nao foi possivel copiar automaticamente.");
    }
  };

  const handleRevoke = async () => {
    if (!revokeTarget) return;

    try {
      setRevokeLoading(true);
      await revokeApiKey(revokeTarget.id);
      setStatus("API Key revogada.");
      setRevokeTarget(null);
      await loadApiKeys();
    } catch (error) {
      setStatus(error?.response?.data?.detail || "Nao foi possivel revogar a API Key.");
    } finally {
      setRevokeLoading(false);
    }
  };

  return (
    <section className="page-block">
      <header className="page-header card proto-hero">
        <div>
          <p className="eyebrow">Integrações</p>
          <h2>API Keys</h2>
          <p className="muted">
            Gere chaves de API para integrar outros sistemas ao projeto com escopos definidos e controle de revogação.
          </p>
        </div>
        <div className="proto-hero-actions">
          <button type="button" className="ghost info-btn" onClick={() => setDocsOpen(true)} aria-label="Abrir documentação">
            <FaCircleInfo aria-hidden="true" />
            Docs
          </button>
        </div>
      </header>

      {status && <p className="status">{status}</p>}

      <section className="stats-grid">
        <article className="card stat-card">
          <h3>Total</h3>
          <strong>{apiKeys.length}</strong>
          <p className="muted">Chaves cadastradas.</p>
        </article>
        <article className="card stat-card">
          <h3>Ativas</h3>
          <strong>{activeCount}</strong>
          <p className="muted">Disponíveis para integração.</p>
        </article>
        <article className="card stat-card emphasis">
          <h3>Revogadas</h3>
          <strong>{revokedCount}</strong>
          <p className="muted">Bloqueadas para uso futuro.</p>
        </article>
      </section>

      <section className="proto-split">
        <article className="card proto-panel">
          <div className="action-head">
            <h3>Nova chave</h3>
          </div>

          <form className="proto-form" onSubmit={handleCreate}>
            <label className="proto-field">
              Nome da integração
              <input
                className="proto-input"
                value={name}
                onChange={(event) => setName(event.target.value)}
                placeholder="Ex: automação RH"
                maxLength={120}
              />
            </label>

            <label className="proto-field">
              Expiração em dias
              <input
                className="proto-input"
                type="number"
                min={1}
                max={365}
                value={expiresInDays}
                onChange={(event) => setExpiresInDays(event.target.value)}
                placeholder="Opcional"
              />
            </label>

            <div className="proto-field">
              <span>Escopos</span>
              <div className="proto-chip-grid">
                {scopeOptions.map((scope) => (
                  <button
                    key={scope}
                    type="button"
                    className={`proto-chip ${selectedScopes.includes(scope) ? "active" : ""}`}
                    onClick={() => toggleScope(scope)}
                  >
                    {scope}
                  </button>
                ))}
              </div>
            </div>

            <div className="row-actions">
              <button type="submit" className="primary" disabled={submitting}>
                <FaSquarePlus aria-hidden="true" /> {submitting ? "Gerando..." : "Gerar chave"}
              </button>
              <button type="button" className="ghost" onClick={() => setSelectedScopes(["files:read"])}>
                Resetar escopos
              </button>
            </div>
          </form>

          {generatedKey ? (
            <div className="proto-secret-box">
              <div>
                <p className="eyebrow">Chave gerada para {generatedLabel}</p>
                <code>{generatedKey}</code>
              </div>
              <button type="button" className="ghost icon-only" aria-label="Copiar chave gerada" onClick={handleCopyGeneratedKey}>
                <FaCopy aria-hidden="true" />
              </button>
            </div>
          ) : null}
        </article>

        <article className="card proto-panel">
          <div className="action-head">
            <h3>Chaves existentes</h3>
            <span className="muted">{apiKeys.length} registros</span>
          </div>

          {loading ? (
            <p className="muted">Carregando API Keys...</p>
          ) : (
            <ul className="proto-key-list">
              {apiKeys.length === 0 && <li className="muted">Nenhuma API Key criada.</li>}
              {apiKeys.map((item) => (
                <li key={item.id} className="proto-key-item">
                  <div className="proto-key-main">
                    <div className="proto-key-icon">
                      <FaKey aria-hidden="true" />
                    </div>
                    <div>
                      <strong>{item.name}</strong>
                      <p className="muted">{item.key_prefix}...{item.key_last4}</p>
                      <div className="proto-chip-grid" style={{ marginTop: "0.35rem" }}>
                        {item.scopes.map((scope) => (
                          <span key={scope} className="proto-chip active">{scope}</span>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="proto-key-meta">
                    <span className={`status-pill ${item.is_active ? "active" : "inactive"}`}>
                      {item.is_active ? "Ativa" : "Revogada"}
                    </span>
                    <span className="muted">
                      <FaClock aria-hidden="true" /> Criada {formatDate(item.created_at)}
                    </span>
                    <span className="muted">Último uso: {formatDate(item.last_used_at)}</span>
                  </div>

                  <div className="row-actions">
                    <button
                      type="button"
                      className="danger"
                      disabled={!item.is_active}
                      onClick={() => setRevokeTarget(item)}
                    >
                      Revogar
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </article>
      </section>

      <ApiKeyDocsModal open={docsOpen} onClose={() => setDocsOpen(false)} />

      <ConfirmModal
        open={Boolean(revokeTarget)}
        title="Revogar API Key"
        description={`Deseja revogar a chave "${revokeTarget?.name || ""}"? Ela deixará de funcionar imediatamente.`}
        confirmLabel="Revogar"
        loading={revokeLoading}
        onCancel={() => setRevokeTarget(null)}
        onConfirm={handleRevoke}
      />
    </section>
  );
}