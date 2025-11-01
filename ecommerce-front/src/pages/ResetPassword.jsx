// src/pages/ResetPassword.jsx
//
// Page de réinitialisation de mot de passe avec token
import React, { useState, useEffect } from "react";
import { useNavigate, useSearchParams, Link } from "react-router-dom";
import { api } from "../lib/api";

export default function ResetPassword() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");

  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [pending, setPending] = useState(false);
  const [tokenValid, setTokenValid] = useState(null);
  const [userEmail, setUserEmail] = useState("");

  useEffect(() => {
    // Vérifier la validité du token au chargement
    if (!token) {
      setError("Token de réinitialisation manquant");
      setTokenValid(false);
      return;
    }

    async function verifyToken() {
      try {
        const response = await api.verifyResetToken({ token });
        if (response.valid) {
          setTokenValid(true);
          setUserEmail(response.email);
        } else {
          setTokenValid(false);
          setError(response.message || "Token invalide ou expiré");
        }
      } catch (err) {
        console.error("Erreur lors de la vérification du token:", err);
        setTokenValid(false);
        setError("Token invalide ou expiré");
      }
    }

    verifyToken();
  }, [token]);

  async function handleSubmit(e) {
    e.preventDefault();

    if (newPassword.length < 6) {
      return setError("Le mot de passe doit contenir au moins 6 caractères");
    }

    if (newPassword !== confirmPassword) {
      return setError("Les mots de passe ne correspondent pas");
    }

    setError("");
    setPending(true);

    try {
      await api.resetPassword({ token, new_password: newPassword });
      setSuccess(true);
      // Rediriger vers la page de connexion après 2 secondes
      setTimeout(() => {
        navigate("/login");
      }, 2000);
    } catch (err) {
      console.error("Erreur lors de la réinitialisation:", err);
      let errorMessage = "Erreur lors de la réinitialisation. Veuillez réessayer.";
      if (err?.message) errorMessage = err.message;
      else if (typeof err === "string") errorMessage = err;
      setError(errorMessage);
    } finally {
      setPending(false);
    }
  }

  // Affichage pendant la vérification du token
  if (tokenValid === null) {
    return (
      <div style={{ padding: 40 }}>
        <h2>Réinitialisation du mot de passe</h2>
        <p>Vérification du token en cours...</p>
      </div>
    );
  }

  // Token invalide
  if (tokenValid === false) {
    return (
      <div style={{ padding: 40 }}>
        <h2>Réinitialisation du mot de passe</h2>
        <div
          style={{
            backgroundColor: "#f8d7da",
            border: "1px solid #f5c2c7",
            color: "#842029",
            padding: 16,
            borderRadius: 8,
            maxWidth: 500,
          }}
        >
          <h3 style={{ margin: "0 0 8px 0" }}>❌ Token invalide</h3>
          <p style={{ margin: "8px 0" }}>
            {error || "Le lien de réinitialisation est invalide ou a expiré."}
          </p>
          <p style={{ margin: "8px 0", fontSize: 12 }}>
            Les liens de réinitialisation expirent après 1 heure pour des raisons de sécurité.
          </p>
          <div style={{ marginTop: 16 }}>
            <Link to="/forgot-password" style={{ color: "#2563eb", textDecoration: "none" }}>
              Demander un nouveau lien →
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Succès
  if (success) {
    return (
      <div style={{ padding: 40 }}>
        <h2>Réinitialisation du mot de passe</h2>
        <div
          style={{
            backgroundColor: "#d4edda",
            border: "1px solid #c3e6cb",
            color: "#155724",
            padding: 16,
            borderRadius: 8,
            maxWidth: 500,
          }}
        >
          <h3 style={{ margin: "0 0 8px 0" }}>✅ Mot de passe réinitialisé !</h3>
          <p style={{ margin: "8px 0" }}>
            Votre mot de passe a été réinitialisé avec succès.
          </p>
          <p style={{ margin: "8px 0", fontSize: 12 }}>
            Vous allez être redirigé vers la page de connexion...
          </p>
        </div>
      </div>
    );
  }

  // Formulaire de réinitialisation
  return (
    <div style={{ padding: 40 }}>
      <h2>Réinitialisation du mot de passe</h2>
      <p style={{ color: "#666", marginBottom: 24 }}>
        Entrez votre nouveau mot de passe pour le compte <strong>{userEmail}</strong>
      </p>

      <form onSubmit={handleSubmit} noValidate style={{ maxWidth: 360 }}>
        <label style={{ display: "block", marginBottom: 8 }}>
          Nouveau mot de passe
          <input
            type="password"
            required
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            placeholder="Minimum 6 caractères"
            style={{
              display: "block",
              width: "100%",
              padding: 8,
              marginTop: 4,
              borderRadius: 4,
              border: "1px solid #ccc",
            }}
          />
        </label>

        <label style={{ display: "block", marginBottom: 8 }}>
          Confirmer le mot de passe
          <input
            type="password"
            required
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="Retapez le mot de passe"
            style={{
              display: "block",
              width: "100%",
              padding: 8,
              marginTop: 4,
              borderRadius: 4,
              border: "1px solid #ccc",
            }}
          />
        </label>

        {error && (
          <p style={{ color: "tomato", marginBottom: 8, fontWeight: "bold" }}>
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={pending}
          style={{
            padding: "10px 16px",
            backgroundColor: "#2563eb",
            color: "white",
            border: "none",
            borderRadius: 4,
            cursor: "pointer",
            fontWeight: "bold",
            marginBottom: 16,
          }}
        >
          {pending ? "Réinitialisation…" : "Réinitialiser le mot de passe"}
        </button>

        <div>
          <Link to="/login" style={{ color: "#2563eb", textDecoration: "none" }}>
            ← Retour à la connexion
          </Link>
        </div>
      </form>
    </div>
  );
}

