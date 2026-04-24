import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { BsDeviceHddFill, BsFillFolderFill, BsFileEarmarkFill } from "react-icons/bs";
import { FaHardDrive } from "react-icons/fa6";
import { clearAuth } from "../api/client";
import AppHeader from "../components/AppHeader";

const menuItems = [
  { to: "/", label: "Visão Geral", end: true, icon: FaHardDrive },
  { to: "/folders", label: "Pastas", icon: BsFillFolderFill },
  { to: "/files", label: "Arquivos", icon: BsFileEarmarkFill },
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
