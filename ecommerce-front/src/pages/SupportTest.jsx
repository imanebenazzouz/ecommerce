// src/pages/SupportTest.jsx
//
// Page de test pour le support: affichage debug et rechargement des fils.
import React, { useState, useEffect } from "react";
import { api } from "../lib/api";
import { useAuth } from "../hooks/useAuth";

export default function SupportTest() {
  const { isAuthenticated, user } = useAuth();
  const [threads, setThreads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    console.log("SupportTest: useEffect triggered");
    console.log("SupportTest: isAuthenticated =", isAuthenticated());
    console.log("SupportTest: user =", user);
    
    if (isAuthenticated()) {
      loadThreads();
    } else {
      setLoading(false);
    }
  }, [isAuthenticated, user]);

  const loadThreads = async () => {
    console.log("SupportTest: loadThreads called");
    try {
      setLoading(true);
      setError(null);
      console.log("SupportTest: calling api.listSupportThreads()");
      const data = await api.listSupportThreads();
      console.log("SupportTest: received data =", data);
      setThreads(data || []);
    } catch (err) {
      console.error("SupportTest: error loading threads:", err);
      setError(`Erreur: ${err.message || "Erreur inconnue"}`);
      setThreads([]);
    } finally {
      setLoading(false);
    }
  };

  console.log("SupportTest: render - loading =", loading, "error =", error, "threads =", threads.length);

  if (!isAuthenticated()) {
    return (
      <div style={{ padding: 40, textAlign: "center" }}>
        <h2>Non connecté</h2>
        <p>Vous devez être connecté pour accéder au support.</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div style={{ padding: 40, textAlign: "center" }}>
        <h2>⏳ Chargement...</h2>
        <p>Chargement des fils de discussion...</p>
      </div>
    );
  }

  return (
    <div style={{ padding: 40 }}>
      <h1>🧪 Test Support</h1>
      
      <div style={{ marginBottom: 20, padding: 16, background: "#f0f8ff", borderRadius: 8 }}>
        <h3>Debug Info:</h3>
        <p><strong>Authentifié:</strong> {isAuthenticated() ? "Oui" : "Non"}</p>
        <p><strong>Utilisateur:</strong> {user ? `${user.first_name} ${user.last_name}` : "Non défini"}</p>
        <p><strong>Admin:</strong> {user?.is_admin ? "Oui" : "Non"}</p>
        <p><strong>Threads:</strong> {threads.length}</p>
        <p><strong>Erreur:</strong> {error || "Aucune"}</p>
      </div>

      {error && (
        <div style={{ 
          background: "#fee", 
          color: "#c33", 
          padding: 16, 
          borderRadius: 8, 
          marginBottom: 20 
        }}>
          <h3>Erreur:</h3>
          <p>{error}</p>
        </div>
      )}

      <div>
        <h2>Fils de discussion ({threads.length})</h2>
        {threads.length === 0 ? (
          <p style={{ color: "#666", textAlign: "center", marginTop: 40 }}>
            Aucun fil de discussion
          </p>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {threads.map((thread) => (
              <div
                key={thread.id}
                style={{
                  padding: 16,
                  border: "1px solid #ddd",
                  borderRadius: 8,
                  background: "white",
                }}
              >
                <h3 style={{ margin: 0, marginBottom: 8 }}>{thread.subject}</h3>
                <p style={{ margin: 0, color: "#666", fontSize: 14 }}>
                  ID: {thread.id.slice(-8)} • 
                  {thread.order_id ? ` Commande: ${thread.order_id.slice(-8)}` : " Demande générale"} • 
                  {thread.closed ? " Fermé" : " Ouvert"}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>

      <div style={{ marginTop: 20 }}>
        <button
          onClick={loadThreads}
          style={{
            background: "#007bff",
            color: "white",
            border: "none",
            padding: "8px 16px",
            borderRadius: 4,
            cursor: "pointer",
          }}
        >
          🔄 Recharger
        </button>
      </div>
    </div>
  );
}
