// src/App.jsx
//
// Point d'entrée UI: fournit AuthProvider, routes, et navigation principale.
import React, { useEffect, useState } from "react";
import { Routes, Route, Link } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthProvider";
import { useAuth } from "./hooks/useAuth";
import ProtectedRoute from "./components/ProtectedRoute";
import Footer from "./components/Footer";
import Catalog from "./pages/Catalog";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Cart from "./pages/Cart";
import Admin from "./pages/Admin";
import Profile from "./pages/Profile";
import Orders from "./pages/Orders";
import OrderDetail from "./pages/OrderDetail";
import AdminOrderDetail from "./pages/AdminOrderDetail";
import Support from "./pages/Support";
import AdminSupport from "./pages/AdminSupport";
import SupportTest from "./pages/SupportTest";
import FAQ from "./pages/FAQ";
import CGV from "./pages/legal/CGV";
import MentionsLegales from "./pages/legal/MentionsLegales";
import Confidentialite from "./pages/legal/Confidentialite";
import Cookies from "./pages/legal/Cookies";
import Retractation from "./pages/legal/Retractation";
import Livraison from "./pages/Livraison";
import PaiementSecurise from "./pages/PaiementSecurise";
import Garanties from "./pages/Garanties";
import "./styles/global.css";

/**
 * Contenu principal de l'application avec navigation et routes protégées.
 * @returns {JSX.Element}
 */
function AppContent() {
  const { user, logout, isAuthenticated, loading } = useAuth();
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

  // Afficher un indicateur de chargement pendant la vérification de l'authentification
  if (loading) {
    return (
      <div style={{ padding: 40, fontFamily: "Arial, sans-serif", textAlign: "center" }}>
        <h2>Chargement...</h2>
        <p>Vérification de votre authentification...</p>
      </div>
    );
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
          borderBottom: "1px solid #e5e7eb",
          paddingBottom: 16,
        }}
      >
        {/* Navigation principale */}
        <Link to="/" style={{ fontWeight: "bold", color: "#1f2937" }}>🏠 Accueil</Link>
        <Link to="/cart">🛒 Panier</Link>

        {/* Navigation pour utilisateurs connectés */}
        {isAuth && (
          <>
            <Link to="/profile">👤 Mon profil</Link>
            <Link to="/orders">📦 Mes commandes</Link>
            <Link to="/support">💬 Support</Link>
          </>
        )}

        {/* Navigation admin */}
        {role === "admin" && (
          <>
            <span style={{ color: "#dc2626", fontWeight: "bold" }}>|</span>
            <Link to="/admin" style={{ color: "#dc2626", fontWeight: "bold" }}>⚙️ Administration</Link>
            <Link to="/admin/support" style={{ color: "#dc2626" }}>📞 Support Admin</Link>
          </>
        )}

        {/* Navigation pour utilisateurs non connectés */}
        {!isAuth && (
          <>
            <Link to="/login" style={{ color: "#059669" }}>🔑 Connexion</Link>
            <Link to="/register" style={{ color: "#059669" }}>📝 Inscription</Link>
          </>
        )}

        {/* Informations utilisateur et déconnexion */}
        {isAuth && (
          <>
            <span style={{ color: "#6b7280", fontSize: "0.9em" }}>
              Connecté en tant que <strong>{role === "admin" ? "Administrateur" : "Client"}</strong>
            </span>
            <button
              onClick={handleLogout}
              className="logout-btn"
              style={{
                background: "#fef2f2",
                color: "#dc2626",
                border: "1px solid #fecaca",
                borderRadius: 6,
                padding: "6px 12px",
                cursor: "pointer",
                fontWeight: "600",
                fontSize: "0.9em"
              }}
              title="Se déconnecter"
            >
              🚪 Déconnexion
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
        <Route path="/profile" element={
          <ProtectedRoute requireAuth={true}>
            <Profile />
          </ProtectedRoute>
        } />
        <Route path="/orders" element={
          <ProtectedRoute requireAuth={true}>
            <Orders />
          </ProtectedRoute>
        } />
        <Route path="/orders/:orderId" element={
          <ProtectedRoute requireAuth={true}>
            <OrderDetail />
          </ProtectedRoute>
        } />
        <Route path="/orders/:orderId/invoice" element={
          <ProtectedRoute requireAuth={true}>
            <OrderDetail />
          </ProtectedRoute>
        } />
        <Route path="/support" element={
          <ProtectedRoute requireAuth={true}>
            <Support />
          </ProtectedRoute>
        } />
        <Route path="/support-test" element={
          <ProtectedRoute requireAuth={true} requireAdmin={true}>
            <SupportTest />
          </ProtectedRoute>
        } />

        {/* ✅ Route Admin (protégée visuellement par le menu) */}
        <Route path="/admin" element={
          <ProtectedRoute requireAuth={true} requireAdmin={true}>
            <Admin />
          </ProtectedRoute>
        } />
        <Route path="/admin/orders/:orderId" element={
          <ProtectedRoute requireAuth={true} requireAdmin={true}>
            <AdminOrderDetail />
          </ProtectedRoute>
        } />
        <Route path="/admin/support" element={
          <ProtectedRoute requireAuth={true} requireAdmin={true}>
            <AdminSupport />
          </ProtectedRoute>
        } />

        {/* ✅ Pages légales et informations */}
        <Route path="/faq" element={<FAQ />} />
        <Route path="/legal/cgv" element={<CGV />} />
        <Route path="/legal/mentions-legales" element={<MentionsLegales />} />
        <Route path="/legal/confidentialite" element={<Confidentialite />} />
        <Route path="/legal/cookies" element={<Cookies />} />
        <Route path="/legal/retractation" element={<Retractation />} />
        <Route path="/livraison" element={<Livraison />} />
        <Route path="/paiement-securise" element={<PaiementSecurise />} />
        <Route path="/garanties" element={<Garanties />} />
      </Routes>

      <Footer />
    </div>
  );
}

/**
 * Racine de l'application: encapsule AppContent dans AuthProvider.
 * @returns {JSX.Element}
 */
export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}