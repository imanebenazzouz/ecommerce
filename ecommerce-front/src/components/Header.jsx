// src/components/Header.jsx
import React from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { setToken as apiSetToken } from "../lib/api"; // si tu l'as

export default function Header() {
  const { isAuthenticated, logout, loading } = useAuth();
  const navigate = useNavigate();

  const linkCls = ({ isActive }) => "nav-link" + (isActive ? " active" : "");

  const handleLogout = () => {
    try { apiSetToken?.(null); } catch {}
    logout();
    navigate("/");
  };

  return (
    <header className="app-header">
      <div className="app-container header-content">
        <NavLink to="/" className="logo">Mon e-commerce 🛍️</NavLink>

        {/* petit état de chargement au démarrage si besoin */}
        {loading ? (
          <ul className="nav-links"><li className="nav-link">…</li></ul>
        ) : (
          <ul className="nav-links">
            <li><NavLink to="/" className={linkCls}>Accueil</NavLink></li>
            <li><NavLink to="/cart" className={linkCls}>Panier</NavLink></li>

            {/* NON connecté → Connexion / Inscription */}
            {!isAuthenticated() && (
              <>
                <li><NavLink to="/login" className={linkCls}>Connexion</NavLink></li>
                <li><NavLink to="/register" className={linkCls}>Inscription</NavLink></li>
              </>
            )}

            {/* CONNECTÉ → Déconnexion (et futurs liens: Profil, Commandes…) */}
            {isAuthenticated() && (
              <li>
                <button className="nav-link btn-secondary logout-btn" onClick={handleLogout}>
                  Déconnexion
                </button>
              </li>
            )}
          </ul>
        )}
      </div>
    </header>
  );
}