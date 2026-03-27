import { NavLink, Outlet, useNavigate } from "react-router-dom";

import { clearAuth } from "../api/client";
import AppHeader from "../components/AppHeader";

const menuItems = [
  { to: "/", label: "Visão Geral", end: true },
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
          <span className="menu-title">Navegacao</span>
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
