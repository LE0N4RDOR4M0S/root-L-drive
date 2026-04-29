export default function ApiKeyDocsModal({ open, onClose }) {
  if (!open) return null;

  const origin = typeof window !== "undefined" ? window.location.origin : "https://api.example.com";
  const curlExample = `curl -X GET "${origin}/api/v1/files?folder_id=<folder-id>" \\
  -H "X-API-Key: <sua-chave>"`;
  const fetchExample = `const response = await fetch("${origin}/api/v1/files", {
  headers: {
    "X-API-Key": "<sua-chave>",
  },
});`;
  const pythonExample = `import requests

response = requests.get(
    "${origin}/api/v1/files",
    headers={"X-API-Key": "<sua-chave>"},
)
print(response.json())`;

  return (
    <div className="modal-overlay" role="presentation" onClick={onClose}>
      <section
        className="card api-docs-modal"
        role="dialog"
        aria-modal="true"
        aria-label="Documentação de integração com API Keys"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="modal-head">
          <div>
            <p className="eyebrow">Documentação</p>
            <h3>Como integrar usando a API Key</h3>
          </div>
          <button type="button" className="ghost" onClick={onClose}>
            Fechar
          </button>
        </div>

        <div className="api-docs-grid">
          <article>
            <h4>Fluxo recomendado</h4>
            <ol className="api-docs-steps">
              <li>Crie a chave nesta tela.</li>
              <li>Copie o valor exibido uma única vez.</li>
              <li>Envie a chave no header `X-API-Key`.</li>
              <li>Use o mesmo usuário dono da chave para acessar os recursos permitidos.</li>
            </ol>
          </article>

          <article>
            <h4>Headers</h4>
            <div className="api-docs-note">`X-API-Key: &lt;sua-chave&gt;`</div>
            <div className="api-docs-note">`Accept: application/json`</div>
          </article>

          <article>
            <h4>cURL</h4>
            <pre className="api-docs-code">{curlExample}</pre>
          </article>

          <article>
            <h4>JavaScript</h4>
            <pre className="api-docs-code">{fetchExample}</pre>
          </article>

          <article>
            <h4>Python</h4>
            <pre className="api-docs-code">{pythonExample}</pre>
          </article>

          <article>
            <h4>Boas práticas</h4>
            <ul className="api-docs-steps">
              <li>Armazene a chave em secret manager ou variável de ambiente.</li>
              <li>Não faça commit da chave em código-fonte.</li>
              <li>Revogue chaves não utilizadas.</li>
              <li>Prefira escopos mínimos necessários para cada integração.</li>
            </ul>
          </article>
        </div>
      </section>
    </div>
  );
}