// src/pages/ForgotPassword.jsx
//
// Page de demande de réinitialisation de mot de passe
import React, { useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [pending, setPending] = useState(false);
  const [resetUrl, setResetUrl] = useState("");

  function isEmail(x) {
    return /\S+@\S+\.\S+/.test(x);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!isEmail(email)) {
      return setError("Format d'email invalide");
    }

    setError("");
    setSuccess(false);
    setPending(true);

    try {
      const response = await api.forgotPassword({ email });
      setSuccess(true);
      // En développement, l'API retourne le lien de réinitialisation
      if (response.reset_url) {
        setResetUrl(response.reset_url);
      }
    } catch (err) {
      console.error("Erreur lors de la demande de réinitialisation:", err);
      setError("Une erreur s'est produite. Veuillez réessayer.");
    } finally {
      setPending(false);
    }
  }

  return (
    <div style={{ padding: 40 }}>
      <h2>Mot de passe oublié</h2>
      <p style={{ color: "#666", marginBottom: 24 }}>
        Entrez votre adresse email et nous vous enverrons un lien pour réinitialiser votre mot de passe.
      </p>

      {!success ? (
        <form onSubmit={handleSubmit} noValidate style={{ maxWidth: 360 }}>
          <label style={{ display: "block", marginBottom: 8 }}>
            Email
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="ex: imane@example.com"
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
            {pending ? "Envoi en cours…" : "Envoyer le lien"}
          </button>

          <div>
            <Link to="/login" style={{ color: "#2563eb", textDecoration: "none" }}>
              ← Retour à la connexion
            </Link>
          </div>
        </form>
      ) : (
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
          <h3 style={{ margin: "0 0 8px 0" }}>✅ Email envoyé !</h3>
          <p style={{ margin: "8px 0" }}>
            Si un compte existe avec l'adresse <strong>{email}</strong>, vous recevrez un email
            avec les instructions pour réinitialiser votre mot de passe.
          </p>
          <p style={{ margin: "8px 0", fontSize: 12 }}>
            Le lien expirera dans 1 heure pour des raisons de sécurité.
          </p>

          {resetUrl && (
            <div
              style={{
                backgroundColor: "#fff3cd",
                border: "1px solid #ffc107",
                padding: 12,
                borderRadius: 4,
                marginTop: 16,
              }}
            >
              <p style={{ margin: "0 0 8px 0", fontWeight: "bold", color: "#856404" }}>
                🧪 Mode développement
              </p>
              <p style={{ margin: "4px 0", fontSize: 12, color: "#856404" }}>
                <a
                  href={resetUrl}
                  style={{ color: "#2563eb", textDecoration: "underline" }}
                >
                  Cliquez ici pour réinitialiser votre mot de passe
                </a>
              </p>
            </div>
          )}

          <div style={{ marginTop: 16 }}>
            <Link to="/login" style={{ color: "#2563eb", textDecoration: "none" }}>
              ← Retour à la connexion
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}

