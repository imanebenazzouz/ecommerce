// src/App.jsx
import React, { useEffect, useState } from "react";
import { Routes, Route, Link } from "react-router-dom";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import Catalog from "./pages/Catalog";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Cart from "./pages/Cart";
import Admin from "./pages/Admin";
import Profile from "./pages/Profile";
import Orders from "./pages/Orders";
import OrderDetail from "./pages/OrderDetail";
import AdminOrderDetail from "./pages/AdminOrderDetail";
import "./styles/global.css";

function AppContent() {
  const { user, logout, isAuthenticated } = useAuth();
  const [role, setRole] = useState(() => localStorage.getItem("role"));

  // Synchronise le rôle quand l'utilisateur change
  useEffect(() => {
    if (user) {
      const userRole = user.is_admin ? "admin" : "user";
      localStorage.setItem("role", userRole);
      setRole(userRole);
    } else {
      localStorage.removeItem("role");
      setRole(null);
    }
  }, [user]);

  // Déconnexion
  function handleLogout() {
    logout();
    window.location.assign("/"); // redirection simple
  }

  const isAuth = isAuthenticated();

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
            <Link to="/orders">Mes commandes</Link>
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

        {/* ✅ Routes utilisateur connecté */}
        <Route path="/profile" element={<Profile />} />
        <Route path="/orders" element={<Orders />} />
        <Route path="/orders/:orderId" element={<OrderDetail />} />
        <Route path="/orders/:orderId/invoice" element={<OrderDetail />} />

        {/* ✅ Route Admin (protégée visuellement par le menu) */}
        <Route path="/admin" element={<Admin />} />
        <Route path="/admin/orders/:orderId" element={<AdminOrderDetail />} />
      </Routes>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}