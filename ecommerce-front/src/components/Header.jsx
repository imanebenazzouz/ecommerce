// src/components/Header.jsx
//
// En-tête principal du site: navigation, état auth et action de déconnexion.
// N'affiche connexion/inscription si non authentifié, sinon bouton déconnexion.
import React from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { setToken as apiSetToken } from "../lib/api"; // si tu l'as

/**
 * En-tête applicatif avec navigation et actions d'authentification.
 * @returns {JSX.Element}
 */
export default function Header() {
  const { isAuthenticated, logout, loading } = useAuth();
  const navigate = useNavigate();

  const linkCls = ({ isActive }) => "nav-link" + (isActive ? " active" : "");

  const handleLogout = () => {
    try { 
      apiSetToken?.(null); 
    } catch {
      // Ignore errors when clearing token
    }
    logout();
    navigate("/");
  };

  return (
    <header className="app-header">
      <div className="app-container header-content">
        <NavLink to="/" className="logo">TechStore 🛍️</NavLink>

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