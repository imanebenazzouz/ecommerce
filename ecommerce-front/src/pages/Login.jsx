import React, { useState } from "react";
import { api } from "../lib/api";

export default function Login() {
  const [email, setEmail] = useState("");
  const [pwd, setPwd] = useState("");
  const [error, setError] = useState("");
  const [pending, setPending] = useState(false);

  // Validation simple du format email
  function isEmail(x) {
    return /\S+@\S+\.\S+/.test(x);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!isEmail(email)) return setError("Format d’email invalide");
    if (!pwd) return setError("Mot de passe obligatoire");

    setError("");
    setPending(true);

    try {
      const res = await api.login({ email, password: pwd });
      // Mémoriser le token JWT
      localStorage.setItem("token", res.token);
      location.href = "/"; // Redirection vers la page d'accueil
    } catch (err) {
      console.error("Erreur login:", err);
      // Récupérer un message d'erreur plus précis
      let errorMessage = "Erreur de connexion, veuillez réessayer.";
      
      if (err?.message) {
        errorMessage = err.message;
      } else if (typeof err === 'string') {
        errorMessage = err;
      } else if (err?.toString) {
        errorMessage = err.toString();
      }
      
      setError(errorMessage);
    } finally {
      setPending(false);
    }
  }

  return (
    <div style={{ padding: 40 }}>
      <h2>Connexion</h2>
      
      {/* Comptes de test pour faciliter le développement */}
      <div style={{ 
        backgroundColor: "#f0f0f0", 
        padding: 16, 
        borderRadius: 8, 
        marginBottom: 20,
        border: "1px solid #ddd"
      }}>
        <h3 style={{ margin: "0 0 8px 0", fontSize: 14 }}>🧪 Comptes de test :</h3>
        <p style={{ margin: "4px 0", fontSize: 12 }}>
          <strong>Admin:</strong> admin@example.com / admin
        </p>
        <p style={{ margin: "4px 0", fontSize: 12 }}>
          <strong>Client:</strong> client@example.com / secret
        </p>
      </div>
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
            }}
          />
        </label>

        <label style={{ display: "block", marginBottom: 8 }}>
          Mot de passe
          <input
            type="password"
            required
            value={pwd}
            onChange={(e) => setPwd(e.target.value)}
            placeholder="••••••••"
            style={{
              display: "block",
              width: "100%",
              padding: 8,
              marginTop: 4,
              borderRadius: 4,
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
            padding: "8px 14px",
            backgroundColor: "#000",
            color: "#fff",
            border: "none",
            borderRadius: 4,
            cursor: "pointer",
          }}
        >
          {pending ? "Connexion…" : "Se connecter"}
        </button>
      </form>
    </div>
  );
}