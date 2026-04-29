import { FaCircleNodes, FaComputer, FaFolderOpen, FaServer, FaUsb } from "react-icons/fa6";

const machines = [
  {
    name: "Home-Workstation",
    status: "Online",
    details: "Windows 11 • agente ativo",
    folders: ["Documentos\\", "Projetos\\", "Finanças\\"],
  },
  {
    name: "Notebook Pessoal",
    status: "Pausada",
    details: "último check-in há 6h",
    folders: ["Fotos\\", "Downloads\\"],
  },
  {
    name: "Servidor Local",
    status: "Offline",
    details: "aguardando reconexão",
    folders: ["Backups\\", "Arquivos Compartilhados\\"],
  },
];

export default function MachinesPage() {
  return (
    <section className="page-block">
      <header className="page-header card proto-hero">
        <div>
          <p className="eyebrow">Integrações</p>
          <h2>Máquinas</h2>
          <p className="muted">
            Protótipo visual do agente local que registra máquinas e expõe apenas diretórios específicos, sem compartilhar a
            máquina inteira.
          </p>
        </div>
        <div className="proto-hero-badge">
          <FaCircleNodes aria-hidden="true" />
          <span>Agente local + diretórios selecionados</span>
        </div>
      </header>

      <section className="proto-split machines-layout">
        <article className="card proto-panel proto-machine-shell">
          <div className="action-head">
            <h3>Matriz de máquinas</h3>
            <span className="muted">estado visual</span>
          </div>

          <div className="proto-machine-grid">
            {machines.map((machine) => (
              <div key={machine.name} className="proto-machine-card">
                <div className="proto-machine-card-head">
                  <div className="proto-machine-icon">
                    <FaComputer aria-hidden="true" />
                  </div>
                  <div>
                    <strong>{machine.name}</strong>
                    <p className="muted">{machine.details}</p>
                  </div>
                </div>

                <div className={`status-pill ${machine.status === "Online" ? "active" : machine.status === "Offline" ? "inactive" : ""}`}>
                  {machine.status}
                </div>

                <div className="proto-folder-stack">
                  {machine.folders.map((folder) => (
                    <div key={folder} className="proto-folder-row">
                      <FaFolderOpen aria-hidden="true" />
                      <span>{folder}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </article>

        <article className="card proto-panel">
          <div className="action-head">
            <h3>Installer / agente</h3>
            <span className="muted">projeto visual</span>
          </div>

          <div className="proto-agent-card">
            <div className="proto-agent-line">
              <FaServer aria-hidden="true" />
              <div>
                <strong>Cadastro da máquina</strong>
                <p className="muted">Nome, identificador e status de conexão.</p>
              </div>
            </div>

            <div className="proto-agent-line">
              <FaUsb aria-hidden="true" />
              <div>
                <strong>Pastas autorizadas</strong>
                <p className="muted">Seleção explícita de diretórios permitidos para acesso remoto.</p>
              </div>
            </div>

            <div className="proto-agent-line">
              <FaCircleNodes aria-hidden="true" />
              <div>
                <strong>Sincronização</strong>
                <p className="muted">Atualização de disponibilidade e inventário das pastas.</p>
              </div>
            </div>
          </div>

          <div className="proto-terminal">
            <div className="proto-terminal-bar">
              <span />
              <span />
              <span />
            </div>
            <code>
              agent install --machine "Home-Workstation" --scope "Documentos, Projetos, Finanças"
              <br />
              agent status --live
            </code>
          </div>

          <div className="row-actions" style={{ marginTop: "1rem" }}>
            <button type="button" className="primary">
              Criar instalador
            </button>
            <button type="button" className="ghost">
              Ver fluxo
            </button>
          </div>
        </article>
      </section>
    </section>
  );
}