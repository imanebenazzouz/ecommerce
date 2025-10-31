import React from 'react';
// Garde de route: impose l'authentification et/ou le rôle admin.
import { useAuth } from '../hooks/useAuth';
import { Link } from 'react-router-dom';

/**
 * Protège une route en imposant l'authentification et/ou le rôle admin.
 * @param {Object} props
 * @param {React.ReactNode} props.children - Contenu à rendre si conditions OK
 * @param {boolean} [props.requireAuth=true] - Exige d'être connecté
 * @param {boolean} [props.requireAdmin=false] - Exige le rôle administrateur
 * @returns {JSX.Element}
 */
export default function ProtectedRoute({ children, requireAuth = true, requireAdmin = false }) {
  const { isAuthenticated, isAdmin, loading } = useAuth();


  // Afficher un indicateur de chargement pendant la vérification de l'authentification
  if (loading) {
    return (
      <div style={{ 
        padding: 40, 
        textAlign: "center",
        minHeight: "60vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center"
      }}>
        <div style={{ 
          width: 40, 
          height: 40, 
          border: "4px solid #f3f4f6", 
          borderTop: "4px solid #2563eb", 
          borderRadius: "50%", 
          animation: "spin 1s linear infinite" 
        }}></div>
        <h2 style={{ marginTop: 16, color: "#6b7280" }}>Chargement...</h2>
        <p style={{ color: "#9ca3af" }}>Vérification de votre authentification...</p>
      </div>
    );
  }

  // Vérifier si l'utilisateur est connecté
  if (requireAuth && !isAuthenticated()) {
    return (
      <div style={{ 
        padding: 40, 
        textAlign: "center",
        minHeight: "60vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center"
      }}>
        <div style={{ fontSize: "4rem", marginBottom: 16 }}>🔒</div>
        <h2 style={{ marginBottom: 8, color: "#1f2937" }}>Accès restreint</h2>
        <p style={{ color: "#6b7280", marginBottom: 24 }}>
          Vous devez être connecté pour accéder à cette page.
        </p>
        <Link 
          to="/login" 
          style={{
            display: "inline-block",
            padding: "12px 24px",
            backgroundColor: "#2563eb",
            color: "white",
            textDecoration: "none",
            borderRadius: "6px",
            fontWeight: "600"
          }}
        >
          Se connecter
        </Link>
      </div>
    );
  }

  // Vérifier si l'utilisateur est admin (si requis)
  if (requireAdmin && !isAdmin()) {
    return (
      <div style={{ 
        padding: 40, 
        textAlign: "center",
        minHeight: "60vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center"
      }}>
        <div style={{ fontSize: "4rem", marginBottom: 16 }}>👑</div>
        <h2 style={{ marginBottom: 8, color: "#1f2937" }}>Accès administrateur requis</h2>
        <p style={{ color: "#6b7280", marginBottom: 24 }}>
          Cette page est réservée aux administrateurs.
        </p>
        <Link 
          to="/" 
          style={{
            display: "inline-block",
            padding: "12px 24px",
            backgroundColor: "#2563eb",
            color: "white",
            textDecoration: "none",
            borderRadius: "6px",
            fontWeight: "600"
          }}
        >
          Retour à l'accueil
        </Link>
      </div>
    );
  }

  // Si tout est OK, afficher le contenu
  return children;
}