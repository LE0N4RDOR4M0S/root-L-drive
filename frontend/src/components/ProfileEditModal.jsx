import { useState } from "react";
import { updateMyProfile, uploadAvatar } from "../api/header.js";

export default function ProfileEditModal({ profile, onClose, onProfileUpdate }) {
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [formData, setFormData] = useState({
    full_name: profile?.full_name || "",
    email: profile?.email || "",
    role: profile?.role || "",
    department: profile?.department || "",
    phone: profile?.phone || "",
    avatar_url: profile?.avatar_url || "",
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleCancel = () => {
    setFormData({
      full_name: profile?.full_name || "",
      email: profile?.email || "",
      role: profile?.role || "",
      department: profile?.department || "",
      phone: profile?.phone || "",
      avatar_url: profile?.avatar_url || "",
    });
    setError(null);
    setSuccess(false);
    setIsEditing(false);
  };

  const handleFileSelect = async (file) => {
    if (!file) return;

    // Validate file type
    const allowedTypes = ["image/jpeg", "image/png", "image/webp", "image/gif"];
    if (!allowedTypes.includes(file.type)) {
      setError("Tipo de arquivo não permitido. Use JPEG, PNG, WebP ou GIF");
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setError("Arquivo muito grande. Máximo 5MB");
      return;
    }

    setIsUploading(true);
    setError(null);

    try {
      const updatedProfile = await uploadAvatar(file);
      setFormData((prev) => ({ ...prev, avatar_url: updatedProfile.avatar_url }));
      setSuccess("Avatar carregado com sucesso!");
      setTimeout(() => setSuccess(false), 2000);
    } catch (err) {
      setError(err.message || "Erro ao fazer upload do avatar");
    } finally {
      setIsUploading(false);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = e.dataTransfer.files;
    if (files && files[0]) {
      handleFileSelect(files[0]);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    setError(null);
    setSuccess(false);

    try {
      // Validate required fields
      if (!formData.full_name.trim()) {
        throw new Error("Nome completo é obrigatório");
      }
      if (formData.full_name.length > 120) {
        throw new Error("Nome completo não pode exceder 120 caracteres");
      }
      if (formData.phone && formData.phone.length > 20) {
        throw new Error("Telefone não pode exceder 20 caracteres");
      }

      // Prepare payload - only send changed fields
      const payload = {};
      if (formData.full_name !== profile.full_name) payload.full_name = formData.full_name;
      if (formData.role !== profile.role) payload.role = formData.role;
      if (formData.department !== profile.department) payload.department = formData.department;
      if (formData.phone !== profile.phone) payload.phone = formData.phone;
      if (formData.avatar_url !== profile.avatar_url) payload.avatar_url = formData.avatar_url;

      if (Object.keys(payload).length === 0) {
        setError("Nenhuma alteração detectada");
        setIsSaving(false);
        return;
      }

      const updated = await updateMyProfile(payload);
      onProfileUpdate(updated);
      setSuccess(true);
      setIsEditing(false);

      // Clear success message after 2 seconds
      setTimeout(() => {
        setSuccess(false);
      }, 2000);
    } catch (err) {
      setError(err.message || "Erro ao atualizar perfil");
    } finally {
      setIsSaving(false);
    }
  };

  if (!isEditing) {
    return (
      <div className="profile-view-mode">
        <div className="profile-photo">
          {formData.avatar_url ? (
            <img src={formData.avatar_url} alt="Avatar" />
          ) : (
            <div className="avatar-placeholder">
              {formData.full_name?.charAt(0)?.toUpperCase() || "P"}
            </div>
          )}
        </div>

        <div className="profile-info">
          <h3>{formData.email}</h3>
          <p className="profile-name">{formData.full_name}</p>
          {formData.role && <p className="profile-role">{formData.role}</p>}
          {formData.department && <p className="profile-department">{formData.department}</p>}
          {formData.phone && <p className="profile-phone">{formData.phone}</p>}
        </div>

        <button
          type="button"
          className="btn-primary"
          onClick={() => setIsEditing(true)}
        >
          Editar Perfil
        </button>
      </div>
    );
  }

  return (
    <div className="profile-edit-mode">
      <h3>Editar Perfil</h3>

      {error && <div className="form-error">{error}</div>}
      {success && <div className="form-success">Perfil atualizado com sucesso!</div>}

      <form className="profile-edit-form" onSubmit={(e) => e.preventDefault()}>
        <div className="form-group">
          <label htmlFor="full_name">Nome Completo *</label>
          <input
            id="full_name"
            type="text"
            name="full_name"
            value={formData.full_name}
            onChange={handleChange}
            placeholder="Seu nome completo"
            disabled={isSaving}
            maxLength="120"
          />
          <span className="char-count">{formData.full_name.length}/120</span>
        </div>

        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            value={formData.email}
            disabled
            title="Email não pode ser alterado"
          />
        </div>

        <div className="form-group">
          <label htmlFor="role">Cargo</label>
          <input
            id="role"
            type="text"
            name="role"
            value={formData.role}
            onChange={handleChange}
            placeholder="Ex: Gerente, Analista"
            disabled={isSaving}
            maxLength="100"
          />
        </div>

        <div className="form-group">
          <label htmlFor="department">Departamento</label>
          <input
            id="department"
            type="text"
            name="department"
            value={formData.department}
            onChange={handleChange}
            placeholder="Ex: TI, Financeiro"
            disabled={isSaving}
            maxLength="100"
          />
        </div>

        <div className="form-group">
          <label htmlFor="phone">Telefone</label>
          <input
            id="phone"
            type="tel"
            name="phone"
            value={formData.phone}
            onChange={handleChange}
            placeholder="Ex: (11) 9999-9999"
            disabled={isSaving}
            maxLength="20"
          />
        </div>

        <div className="form-group">
          <label htmlFor="avatar_url">URL do Avatar</label>
          <input
            id="avatar_url"
            type="url"
            name="avatar_url"
            value={formData.avatar_url}
            onChange={handleChange}
            placeholder="https://example.com/avatar.jpg"
            disabled={isSaving}
          />
          {formData.avatar_url && (
            <div className="avatar-preview">
              <img src={formData.avatar_url} alt="Preview" onError={(e) => (e.target.style.display = "none")} />
            </div>
          )}
        </div>

        <div className="form-group">
          <label>Fazer upload de nova foto</label>
          <div
            className={`avatar-upload-area ${dragActive ? "drag-active" : ""} ${isUploading ? "uploading" : ""}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <input
              type="file"
              id="avatar-file"
              accept="image/jpeg,image/png,image/webp,image/gif"
              onChange={(e) => handleFileSelect(e.target.files?.[0])}
              disabled={isUploading}
              style={{ display: "none" }}
            />
            <label htmlFor="avatar-file" className="upload-label">
              {isUploading ? (
                <span>Carregando...</span>
              ) : (
                <>
                  <span className="upload-icon">📸</span>
                  <span className="upload-text">Arraste uma imagem aqui ou clique para selecionar</span>
                  <span className="upload-hint">JPG, PNG, WebP ou GIF (máximo 5MB)</span>
                </>
              )}
            </label>
          </div>
        </div>

        <div className="form-actions">
          <button
            type="button"
            className="btn-secondary"
            onClick={handleCancel}
            disabled={isSaving}
          >
            Cancelar
          </button>
          <button
            type="button"
            className="btn-primary"
            onClick={handleSave}
            disabled={isSaving}
          >
            {isSaving ? "Salvando..." : "Salvar Alterações"}
          </button>
        </div>
      </form>
    </div>
  );
}
