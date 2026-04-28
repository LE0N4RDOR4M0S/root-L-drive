import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { BsFillFolderFill, BsFileEarmarkFill } from "react-icons/bs";
import { FaHardDrive, FaComputer, FaKey, FaTrash, FaShare, FaStar } from "react-icons/fa6";
import { clearAuth } from "../api/client";
import AppHeader from "../components/AppHeader";

const overviewMenuItem = {
  to: "/",
  label: "Visão Geral",
  end: true,
  icon: FaHardDrive,
  children: [
    { to: "/folders", label: "Pastas", icon: BsFillFolderFill },
    { to: "/files", label: "Arquivos", icon: BsFileEarmarkFill },
  ],
};

const menuItems = [overviewMenuItem,
  { to: "/favorites", label: "Favoritos", icon: FaStar },
  { to: "/trash", label: "Lixeira", icon: FaTrash }];

const integrationItems = [
  { to: "/integrations/apikeys", label: "API Keys", icon: FaKey },
  { to: "/integrations/machines", label: "Máquinas", icon: FaComputer },
];

const toolItems = [
  { to: "/tools/shared", label: "Links Compartilhados", icon: FaShare },
];

export default function AppLayout() {
  const navigate = useNavigate();

  const handleLogout = () => {
    clearAuth();
    navigate("/login");
  };

  return (
    <div className="app-shell">
      <aside className="sidebar card">
        <div className="brand">
          <span className="brand-kicker">Workspace Cloud</span>
          <h1>Root L Drive</h1>
        </div>

        <nav className="menu">
          <span className="menu-title">Navegação</span>
          {menuItems.map((item) => (
            <div key={item.to} className="menu-group">
              <NavLink
                to={item.to}
                end={item.end}
                className={({ isActive }) => `menu-link ${isActive ? "active" : ""}`}
              >
                <item.icon className="menu-link-icon" aria-hidden="true" />
                {item.label}
              </NavLink>

              {item.children ? (
                <div className="menu-subitems" aria-label={`${item.label} atalhos`}>
                  {item.children.map((child) => (
                    <NavLink
                      key={child.to}
                      to={child.to}
                      className={({ isActive }) => `menu-sublink ${isActive ? "active" : ""}`}
                    >
                      <child.icon className="menu-link-icon" aria-hidden="true" />
                      {child.label}
                    </NavLink>
                  ))}
                </div>
              ) : null}
            </div>
          ))}
          <span className="menu-title">Integrações</span>
          {integrationItems.map((item) => (
            (() => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.end}
                  className={({ isActive }) => `menu-link ${isActive ? "active" : ""}`}
                >
                  <Icon className="menu-link-icon" aria-hidden="true" />
                  {item.label}
                </NavLink>
              );
            })()
          ))}

          <span className="menu-title">Ferramentas</span>
          {toolItems.map((item) => (
            (() => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.end}
                  className={({ isActive }) => `menu-link ${isActive ? "active" : ""}`}
                >
                  <Icon className="menu-link-icon" aria-hidden="true" />
                  {item.label}
                </NavLink>
              );
            })()
          ))}
        </nav>

        <div className="sidebar-footer">
          <button className="ghost logout-btn" onClick={handleLogout}>
            Sair
          </button>
        </div>
      </aside>

      <main className="content-area">
        <AppHeader />
        <Outlet />
      </main>
    </div>
  );
}
