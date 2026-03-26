import { NavLink, Outlet, useNavigate } from "react-router-dom";

import { clearAuth } from "../api/client";

const menuItems = [
  { to: "/", label: "Visao Geral", end: true },
  { to: "/folders", label: "Pastas" },
  { to: "/files", label: "Arquivos" },
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
          {menuItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) => `menu-link ${isActive ? "active" : ""}`}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <button className="ghost logout-btn" onClick={handleLogout}>
          Sair
        </button>
      </aside>

      <main className="content-area">
        <header className="topbar card">
          <div>
            <h2>Painel Operacional</h2>
          </div>
          <span className="topbar-badge">Ambiente Pessoal</span>
        </header>
        <Outlet />
      </main>
    </div>
  );
}
