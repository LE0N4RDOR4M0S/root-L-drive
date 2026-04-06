import { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import {
  deleteAllNotifications,
  deleteNotification,
  getMyProfile,
  listNotifications,
  markAllNotificationsAsRead,
  markNotificationAsRead,
  searchWorkspace,
} from "../api/header";
import ProfileEditModal from "./ProfileEditModal";
import SemanticSearchModal from "./SemanticSearchModal";

const pathLabels = {
  "/": "Visão Geral",
  "/folders": "Pastas",
  "/files": "Arquivos",
};

export default function AppHeader() {
  const location = useLocation();
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [searchResults, setSearchResults] = useState({ folders: [], files: [] });
  const [searchLoading, setSearchLoading] = useState(false);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [isNotifOpen, setIsNotifOpen] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [profile, setProfile] = useState(null);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [showProfileEdit, setShowProfileEdit] = useState(false);
  const [isSemanticSearchOpen, setIsSemanticSearchOpen] = useState(false);

  const activeLabel = useMemo(() => {
    return pathLabels[location.pathname] ?? "Painel";
  }, [location.pathname]);

  const totalSearchResults = searchResults.folders.length + searchResults.files.length;

  useEffect(() => {
    async function bootstrapHeader() {
      try {
        const [profileData, notificationsData] = await Promise.all([getMyProfile(), listNotifications(10)]);
        setProfile(profileData);
        setNotifications(notificationsData.items || []);
        setUnreadCount(notificationsData.unread_count || 0);
      } catch {
        setNotifications([]);
      }
    }

    bootstrapHeader();
  }, []);

  useEffect(() => {
    const cleanQuery = query.trim();
    if (cleanQuery.length < 2) {
      setSearchResults({ folders: [], files: [] });
      return;
    }

    const timeoutId = setTimeout(async () => {
      try {
        setSearchLoading(true);
        const data = await searchWorkspace(cleanQuery, 6);
        setSearchResults({
          folders: data.folders || [],
          files: data.files || [],
        });
        setIsSearchOpen(true);
      } catch {
        setSearchResults({ folders: [], files: [] });
      } finally {
        setSearchLoading(false);
      }
    }, 260);

    return () => clearTimeout(timeoutId);
  }, [query]);

  const handleSearch = (event) => {
    event.preventDefault();
    if (!query.trim()) {
      return;
    }

    navigate(`/files?search=${encodeURIComponent(query.trim())}`);
    setIsSearchOpen(false);
  };

  const handleNotificationRead = async (notificationId) => {
    try {
      await markNotificationAsRead(notificationId);
      setNotifications((current) =>
        current.map((item) => (item.id === notificationId ? { ...item, is_read: true } : item))
      );
      setUnreadCount((current) => Math.max(0, current - 1));
    } catch {
      // noop
    }
  };

  const handleReadAll = async () => {
    try {
      await markAllNotificationsAsRead();
      setNotifications((current) => current.map((item) => ({ ...item, is_read: true })));
      setUnreadCount(0);
    } catch {
      // noop
    }
  };

  const handleDeleteNotification = async (notificationId) => {
    try {
      await deleteNotification(notificationId);
      setNotifications((current) => current.filter((item) => item.id !== notificationId));
    } catch {
      // noop
    }
  };

  const handleDeleteAllNotifications = async () => {
    if (!confirm("Tem certeza que deseja deletar todas as notificações?")) {
      return;
    }
    try {
      await deleteAllNotifications();
      setNotifications([]);
      setUnreadCount(0);
    } catch {
      // noop
    }
  };

  const openSearchResult = (item) => {
    const target = item.kind === "folder" ? "/folders" : "/files";
    navigate(`${target}?search=${encodeURIComponent(item.name)}`);
    setQuery(item.name);
    setIsSearchOpen(false);
  };

  const fallbackProfileName = profile?.full_name || profile?.email || "Meu Perfil";
  const profileInitial = fallbackProfileName?.charAt(0)?.toUpperCase() || "P";

  const lastLoginText = profile?.last_login_at
    ? new Date(profile.last_login_at).toLocaleString("pt-BR")
    : "Sem acesso recente";

  const profileSinceText = profile?.created_at
    ? new Date(profile.created_at).toLocaleDateString("pt-BR")
    : "-";

  const notifCounter = unreadCount > 99 ? "99+" : String(unreadCount);

  const searchItems = [
    ...searchResults.folders.map((item) => ({ ...item, kind: "folder" })),
    ...searchResults.files.map((item) => ({ ...item, kind: "file" })),
  ];

  const profileLabel = profile?.role ? `${profile.role} • ${profile.department || "Setor"}` : "Ambiente Pessoal";

  const handleSearchFocus = () => {
    if (query.trim().length >= 2) {
      setIsSearchOpen(true);
    }
  };

  return (
    <header className="app-header card">
      <form className="header-search" onSubmit={handleSearch}>
        <span className="header-search-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" role="presentation" focusable="false">
            <circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" strokeWidth="1.8" />
            <path d="M16.5 16.5L21 21" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
          </svg>
        </span>
        <input
          type="search"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          onFocus={handleSearchFocus}
          placeholder="Buscar por nome de pasta ou arquivo"
          aria-label="Buscar por nome de pasta ou arquivo"
        />

        {isSearchOpen ? (
          <div className="header-search-dropdown" role="listbox" aria-label="Resultados da busca">
            {searchLoading ? <p className="muted">Buscando...</p> : null}
            {!searchLoading && totalSearchResults === 0 ? <p className="muted">Nenhum resultado encontrado.</p> : null}
            {!searchLoading
              ? searchItems.map((item) => (
                  <button
                    key={`${item.kind}-${item.id}`}
                    type="button"
                    className="search-result-item"
                    onClick={() => openSearchResult(item)}
                  >
                    <span className={`search-kind ${item.kind}`}>{item.kind === "folder" ? "Pasta" : "Arquivo"}</span>
                    <strong>{item.name}</strong>
                  </button>
                ))
              : null}
          </div>
        ) : null}
      </form>

      <div className="header-tools">
        <button
          type="button"
          className="icon-btn semantic-search-btn"
          onClick={() => setIsSemanticSearchOpen(true)}
          title="Busca semântica por conteúdo"
          aria-label="Busca semântica"
        >
          <span aria-hidden="true" className="icon-wrap">
            <svg viewBox="0 0 24 24" role="presentation" focusable="false">
              {/* Lupa com símbolo de IA */}
              <circle cx="9" cy="9" r="6" fill="none" stroke="currentColor" strokeWidth="1.8" />
              <path d="M13 13l6 6" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
              {/* Estrela/AI symbol */}
              <path d="M15 8l1 3h3l-2 2 1 3-3-2-3 2 1-3-2-2h3z" fill="currentColor" opacity="0.4" />
            </svg>
          </span>
        </button>

        <SemanticSearchModal 
          isOpen={isSemanticSearchOpen}
          onClose={() => setIsSemanticSearchOpen(false)}
        />

        <div className={`notif-panel ${isNotifOpen ? "open" : ""}`}>
          <button
            type="button"
            className="icon-btn"
            onClick={() => setIsNotifOpen((current) => !current)}
            aria-expanded={isNotifOpen}
            aria-label="Abrir notificações"
          >
            <span aria-hidden="true" className="icon-wrap">
              <svg viewBox="0 0 24 24" role="presentation" focusable="false">
                <path
                  d="M12 4a4 4 0 00-4 4v2.3c0 1.2-.4 2.4-1.2 3.3L5.5 15h13l-1.3-1.4a5 5 0 01-1.2-3.3V8a4 4 0 00-4-4z"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.7"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
                <path d="M10 18a2 2 0 004 0" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
              </svg>
            </span>
            {unreadCount > 0 ? <span className="notif-count">{notifCounter}</span> : null}
          </button>

          {isNotifOpen ? (
            <div className="notif-dropdown" role="dialog" aria-label="Notificações">
              <div className="notif-head">
                <strong>Notificações</strong>
                <div className="notif-head-actions">
                  {notifications.length > 0 && unreadCount > 0 && (
                    <button type="button" className="link-btn" onClick={handleReadAll}>
                      Marcar todas
                    </button>
                  )}
                  {notifications.length > 0 && (
                    <button type="button" className="link-btn delete-all-btn" onClick={handleDeleteAllNotifications}>
                      Limpar tudo
                    </button>
                  )}
                </div>
              </div>
              <ul>
                {notifications.length === 0 ? <li>Nenhuma notificação no momento.</li> : null}
                {notifications.map((item) => (
                  <li key={item.id} className={item.is_read ? "read" : "unread"}>
                    <button type="button" className="notif-item" onClick={() => handleNotificationRead(item.id)}>
                      <strong>{item.title}</strong>
                      <span>{item.message}</span>
                    </button>
                    <button
                      type="button"
                      className="notif-delete-btn"
                      onClick={() => handleDeleteNotification(item.id)}
                      aria-label="Deletar notificação"
                      title="Deletar"
                    >
                      ✕
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
        </div>

        <button
          type="button"
          className="profile-btn"
          aria-label="Abrir perfil"
          aria-expanded={isProfileOpen}
          onClick={() => setIsProfileOpen((current) => !current)}
        >
          <span className="profile-avatar" aria-hidden="true">
            {profileInitial}
          </span>
          <span className="profile-meta">
            <strong>{fallbackProfileName}</strong>
            <small>{profileLabel}</small>
          </span>
        </button>

        {isProfileOpen ? (
          <div className="profile-dropdown" role="dialog" aria-label="Meu perfil">
            {showProfileEdit ? (
              <ProfileEditModal
                profile={profile}
                onClose={() => setShowProfileEdit(false)}
                onProfileUpdate={(updated) => {
                  setProfile(updated);
                  setShowProfileEdit(false);
                }}
              />
            ) : (
              <>
                <div className="profile-view-header">
                  <h4>{profile?.full_name || profile?.email || "Meu Perfil"}</h4>
                  <button
                    type="button"
                    className="link-btn edit-profile-btn"
                    onClick={() => setShowProfileEdit(true)}
                  >
                    Editar
                  </button>
                </div>
                <p>{profile?.email || "-"}</p>
                <ul>
                  {profile?.role && (
                    <li>
                      <strong>Funcao:</strong> {profile.role}
                    </li>
                  )}
                  {profile?.department && (
                    <li>
                      <strong>Setor:</strong> {profile.department}
                    </li>
                  )}
                  {profile?.phone && (
                    <li>
                      <strong>Telefone:</strong> {profile.phone}
                    </li>
                  )}
                  <li>
                    <strong>Ultimo acesso:</strong>{" "}
                    {profile?.last_login_at ? new Date(profile.last_login_at).toLocaleString("pt-BR") : "Sem acesso recente"}
                  </li>
                  <li>
                    <strong>Membro desde:</strong>{" "}
                    {profile?.created_at ? new Date(profile.created_at).toLocaleDateString("pt-BR") : "-"}
                  </li>
                  <li>
                    <strong>Contexto atual:</strong> {activeLabel}
                  </li>
                </ul>
              </>
            )}
          </div>
        ) : null}
      </div>
    </header>
  );
}
