// src/pages/Profile.jsx
//
// Page profil: affichage/modification du prénom, nom et adresse avec validations.
import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { validateAddress, validateName } from "../utils/validations";

export default function Profile() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [user, setUser] = useState(null);
  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
    address: "",
  });

  // Unauthorized UI (no token at all)
  const hasToken = !!localStorage.getItem("token");

  useEffect(() => {
    let ignore = false;
    async function fetchMe() {
      setLoading(true);
      setError("");
      setSuccess("");
      try {
        const me = await api.me();
        if (ignore) return;
        setUser(me);
        setForm({
          first_name: me.first_name || "",
          last_name: me.last_name || "",
          address: me.address || "",
        });
      } catch (err) {
        if (ignore) return;
        const msg = err?.message || "Erreur lors du chargement du profil";
        setError(msg);
      } finally {
        if (!ignore) setLoading(false);
      }
    }
    if (hasToken) fetchMe();
    else setLoading(false);
    return () => {
      ignore = true;
    };
  }, [hasToken]);

  function onChange(e) {
    const { name, value } = e.target;
    setForm((f) => ({ ...f, [name]: value }));
  }

  async function onSubmit(e) {
    e.preventDefault();
    if (!hasToken) return; // guard
    
    // Validation côté client
    if (!form.first_name?.trim()) {
      setError("Le prénom est requis");
      return;
    }
    if (!form.last_name?.trim()) {
      setError("Le nom est requis");
      return;
    }
    
    // Valider le prénom (pas de chiffres)
    const firstNameValidation = validateName(form.first_name, "Prénom");
    if (!firstNameValidation.valid) {
      setError(firstNameValidation.error);
      return;
    }
    
    // Valider le nom (pas de chiffres)
    const lastNameValidation = validateName(form.last_name, "Nom");
    if (!lastNameValidation.valid) {
      setError(lastNameValidation.error);
      return;
    }
    
    // Valider l'adresse
    const addressValidation = validateAddress(form.address);
    if (!addressValidation.valid) {
      setError(addressValidation.error);
      return;
    }
    
    setSaving(true);
    setError("");
    setSuccess("");
    try {
      const updated = await api.updateProfile({
        first_name: form.first_name,
        last_name: form.last_name,
        address: form.address,
      });
      setUser(updated);
      setForm({
        first_name: updated.first_name || "",
        last_name: updated.last_name || "",
        address: updated.address || "",
      });
      setSuccess("Profil mis à jour");
    } catch (err) {
      let msg = "Échec de la mise à jour";
      if (err?.message) msg = err.message;
      setError(msg);
    } finally {
      setSaving(false);
    }
  }

  // Not authenticated → friendly 401 panel
  if (!hasToken) {
    return (
      <div style={{ padding: 40 }}>
        <h2>Mon profil</h2>
        <div
          style={{
            marginTop: 12,
            padding: 16,
            border: "1px solid #f3c6c6",
            background: "#fff5f5",
            borderRadius: 8,
          }}
        >
          <p style={{ margin: 0 }}>
            <strong>401</strong> – Vous devez être connecté pour accéder à cette page.
          </p>
          <p style={{ marginTop: 8 }}>
            <Link to="/login">Aller à la connexion</Link>
          </p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: 40 }}>
      <h2>Mon profil</h2>

      {loading && (
        <p aria-live="polite" style={{ color: "#555" }}>Chargement…</p>
      )}

      {!loading && error && (
        <div
          role="alert"
          style={{
            margin: "12px 0",
            padding: 12,
            border: "1px solid #f3c6c6",
            background: "#fff5f5",
            borderRadius: 8,
            color: "#b91c1c",
          }}
        >
          {error}
          {String(error).includes("401") && (
            <div style={{ marginTop: 8 }}>
              <Link to="/login">Se connecter</Link>
            </div>
          )}
        </div>
      )}

      {!loading && user && (
        <form onSubmit={onSubmit} noValidate style={{ maxWidth: 520 }}>
          <fieldset disabled={saving} style={{ border: "none", padding: 0, margin: 0 }}>
            <div style={{ display: "grid", gap: 12 }}>
              <label>
                Email (lecture seule)
                <input
                  type="email"
                  value={user.email || ""}
                  readOnly
                  aria-readonly="true"
                  style={inputStyle}
                />
              </label>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                <label>
                  Prénom
                  <input
                    name="first_name"
                    value={form.first_name}
                    onChange={onChange}
                    style={inputStyle}
                    placeholder="Votre prénom"
                    autoComplete="given-name"
                  />
                </label>
                <label>
                  Nom
                  <input
                    name="last_name"
                    value={form.last_name}
                    onChange={onChange}
                    style={inputStyle}
                    placeholder="Votre nom"
                    autoComplete="family-name"
                  />
                </label>
              </div>

              <label>
                Adresse
                <textarea
                  name="address"
                  value={form.address}
                  onChange={onChange}
                  rows={3}
                  style={{ ...inputStyle, resize: "vertical" }}
                  placeholder="Ex: 12 Rue des Fleurs, 75001 Paris"
                  autoComplete="street-address"
                  aria-describedby="address-help"
                />
                <small id="address-help" style={{ fontSize: 12, color: "#6b7280", display: "block", marginTop: 4 }}>
                  Format attendu : numéro de rue, nom de rue, code postal, ville
                </small>
              </label>

              <div>
                <span style={{ fontSize: 14, color: "#555" }}>
                  Rôle: <strong>{user.is_admin ? "admin" : "client"}</strong>
                </span>
              </div>

              {success && (
                <div
                  role="status"
                  aria-live="polite"
                  style={{
                    padding: 10,
                    background: "#ecfdf5",
                    border: "1px solid #a7f3d0",
                    color: "#065f46",
                    borderRadius: 6,
                  }}
                >
                  {success}
                </div>
              )}

              {error && !loading && (
                <div
                  role="alert"
                  style={{
                    padding: 10,
                    background: "#fff5f5",
                    border: "1px solid #f3c6c6",
                    color: "#b91c1c",
                    borderRadius: 6,
                  }}
                >
                  {error}
                </div>
              )}

              <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
                <button
                  type="submit"
                  disabled={saving}
                  style={buttonPrimary}
                >
                  {saving ? "Enregistrement…" : "Enregistrer"}
                </button>
                <small style={{ color: "#6b7280" }}>
                  Seuls prénom, nom et adresse sont modifiables.
                </small>
              </div>
            </div>
          </fieldset>
        </form>
      )}
    </div>
  );
}

const inputStyle = {
  display: "block",
  width: "100%",
  padding: 10,
  marginTop: 4,
  borderRadius: 6,
  border: "1px solid #d1d5db",
  fontSize: 14,
};

const buttonPrimary = {
  padding: "10px 16px",
  backgroundColor: "#2563eb",
  color: "white",
  border: "none",
  borderRadius: 6,
  cursor: "pointer",
  fontWeight: "bold",
};