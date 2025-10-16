// src/App.jsx
import React, { useEffect, useState } from "react";
import { Routes, Route, Link } from "react-router-dom";
import Catalog from "./pages/Catalog";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Cart from "./pages/Cart";
import Admin from "./pages/Admin";
import Profile from "./pages/Profile"; // ✅ AJOUT
import "./styles/global.css";

export default function App() {
  // États locaux pour l’authentification et le rôle
  const [isAuth, setIsAuth] = useState(() => !!localStorage.getItem("token"));
  const [role, setRole] = useState(() => localStorage.getItem("role"));

  // Synchronise token + rôle entre les onglets ou après un refresh
  useEffect(() => {
    const sync = () => {
      setIsAuth(!!localStorage.getItem("token"));
      setRole(localStorage.getItem("role"));
    };
    window.addEventListener("storage", sync);
    window.addEventListener("focus", sync);
    return () => {
      window.removeEventListener("storage", sync);
      window.removeEventListener("focus", sync);
    };
  }, []);

  // Déconnexion
  function handleLogout() {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    setIsAuth(false);
    setRole(null);
    window.location.assign("/"); // redirection simple
  }

  return (
    <div style={{ padding: 40, fontFamily: "Arial, sans-serif" }}>
      <nav
        style={{
          marginBottom: 24,
          display: "flex",
          gap: 16,
          alignItems: "center",
          flexWrap: "wrap",
        }}
      >
        <Link to="/">Accueil</Link>
        <Link to="/cart">Panier</Link>

        {/* ✅ Lien Profil visible UNIQUEMENT si connecté (user ou admin) */}
        {isAuth && <Link to="/profile">Mon profil</Link>}

        {/* ✅ Si admin connecté, affiche lien Admin */}
        {role === "admin" && <Link to="/admin">Admin</Link>}

        {/* ✅ Si pas connecté → Connexion / Inscription */}
        {!isAuth && (
          <>
            <Link to="/login">Connexion</Link>
            <Link to="/register">Inscription</Link>
          </>
        )}

        {/* ✅ Si connecté → affichage rôle + bouton Déconnexion */}
        {isAuth && (
          <>
            <span style={{ color: "#555" }}>
              Connecté ({role === "admin" ? "admin" : "client"})
            </span>
            <button
              onClick={handleLogout}
              style={{
                background: "transparent",
                border: "1px solid #ddd",
                borderRadius: 6,
                padding: "4px 10px",
                cursor: "pointer",
              }}
              title="Se déconnecter"
            >
              Déconnexion
            </button>
          </>
        )}
      </nav>

      <h1>Mon e-commerce 🛍️</h1>

      <Routes>
        <Route path="/" element={<Catalog />} />
        <Route path="/cart" element={<Cart />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* ✅ Route Profil */}
        <Route path="/profile" element={<Profile />} />

        {/* ✅ Route Admin (protégée visuellement par le menu) */}
        <Route path="/admin" element={<Admin />} />
      </Routes>
    </div>
  );
}