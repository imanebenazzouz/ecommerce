// src/pages/AdminSupport.jsx
import React, { useState, useEffect } from "react";
import { api } from "../lib/api";
import { useAuth } from "../contexts/AuthContext";

export default function AdminSupport() {
  const { user, isAuthenticated } = useAuth();
  const [threads, setThreads] = useState([]);
  const [selectedThread, setSelectedThread] = useState(null);
  const [newMessage, setNewMessage] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState("all"); // all, open, closed

  // Charger les threads au montage
  useEffect(() => {
    loadThreads();
  }, []);

  const loadThreads = async () => {
    try {
      setLoading(true);
      const data = await api.adminListSupportThreads();
      setThreads(data);
      setError(null);
    } catch (err) {
      setError("Erreur lors du chargement des fils de discussion");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadThread = async (threadId) => {
    try {
      const data = await api.adminGetSupportThread(threadId);
      setSelectedThread(data);
    } catch (err) {
      setError("Erreur lors du chargement du fil");
      console.error(err);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !selectedThread) return;

    try {
      const data = await api.adminPostSupportMessage(selectedThread.id, {
        content: newMessage,
      });
      
      // Mettre à jour le thread avec le nouveau message
      const updatedThread = {
        ...selectedThread,
        messages: [...selectedThread.messages, data],
      };
      setSelectedThread(updatedThread);
      setNewMessage("");
      setError(null);
    } catch (err) {
      setError("Erreur lors de l'envoi du message");
      console.error(err);
    }
  };

  const closeThread = async (threadId) => {
    if (!confirm("Êtes-vous sûr de vouloir fermer ce fil de discussion ?")) return;

    try {
      await api.adminCloseSupportThread(threadId);
      await loadThreads(); // Recharger la liste
      if (selectedThread?.id === threadId) {
        setSelectedThread(null);
      }
      setError(null);
    } catch (err) {
      setError("Erreur lors de la fermeture du fil");
      console.error(err);
    }
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp * 1000).toLocaleString("fr-FR");
  };

  // Filtrer les threads
  const filteredThreads = threads.filter(thread => {
    if (filter === "open") return !thread.closed;
    if (filter === "closed") return thread.closed;
    return true;
  });

  // Vérifier l'authentification et les droits admin
  if (!isAuthenticated()) {
    return (
      <div style={{ textAlign: "center", padding: 40 }}>
        <h2>Accès refusé</h2>
        <p>Vous devez être connecté pour accéder au support admin.</p>
      </div>
    );
  }

  if (!user?.is_admin) {
    return (
      <div style={{ textAlign: "center", padding: 40 }}>
        <h2>Accès refusé</h2>
        <p>Seuls les administrateurs peuvent accéder à cette page.</p>
      </div>
    );
  }

  if (loading) {
    return <div>Chargement des fils de discussion...</div>;
  }

  return (
    <div style={{ maxWidth: 1400, margin: "0 auto", padding: 20 }}>
      <h1>🛠️ Support Admin</h1>
      
      {error && (
        <div style={{ 
          background: "#fee", 
          color: "#c33", 
          padding: 10, 
          borderRadius: 4, 
          marginBottom: 20 
        }}>
          {error}
        </div>
      )}

      <div style={{ display: "flex", gap: 20, height: "70vh" }}>
        {/* Liste des threads */}
        <div style={{ flex: 1, border: "1px solid #ddd", borderRadius: 8, padding: 16 }}>
          <div style={{ marginBottom: 16 }}>
            <h2 style={{ margin: 0, marginBottom: 12 }}>Tous les fils</h2>
            <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
              <button
                onClick={() => setFilter("all")}
                style={{
                  padding: "4px 12px",
                  border: "1px solid #ddd",
                  background: filter === "all" ? "#007bff" : "white",
                  color: filter === "all" ? "white" : "black",
                  borderRadius: 4,
                  cursor: "pointer",
                }}
              >
                Tous ({threads.length})
              </button>
              <button
                onClick={() => setFilter("open")}
                style={{
                  padding: "4px 12px",
                  border: "1px solid #ddd",
                  background: filter === "open" ? "#007bff" : "white",
                  color: filter === "open" ? "white" : "black",
                  borderRadius: 4,
                  cursor: "pointer",
                }}
              >
                Ouverts ({threads.filter(t => !t.closed).length})
              </button>
              <button
                onClick={() => setFilter("closed")}
                style={{
                  padding: "4px 12px",
                  border: "1px solid #ddd",
                  background: filter === "closed" ? "#007bff" : "white",
                  color: filter === "closed" ? "white" : "black",
                  borderRadius: 4,
                  cursor: "pointer",
                }}
              >
                Fermés ({threads.filter(t => t.closed).length})
              </button>
            </div>
          </div>

          {filteredThreads.length === 0 ? (
            <p style={{ color: "#666", textAlign: "center", marginTop: 40 }}>
              Aucun fil de discussion
            </p>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {filteredThreads.map((thread) => (
                <div
                  key={thread.id}
                  onClick={() => loadThread(thread.id)}
                  style={{
                    padding: 12,
                    border: "1px solid #eee",
                    borderRadius: 6,
                    cursor: "pointer",
                    background: selectedThread?.id === thread.id ? "#f0f8ff" : "white",
                    borderLeft: selectedThread?.id === thread.id ? "4px solid #007bff" : "4px solid transparent",
                  }}
                >
                  <div style={{ fontWeight: "bold", marginBottom: 4 }}>
                    {thread.subject}
                  </div>
                  <div style={{ fontSize: 12, color: "#666", marginBottom: 4 }}>
                    Client: {thread.user_id.slice(-8)} • {thread.messages.length} message(s)
                  </div>
                  <div style={{ fontSize: 12, color: "#666" }}>
                    {thread.order_id ? `Commande #${thread.order_id.slice(-8)}` : "Demande générale"}
                    {thread.closed && " • 🔒 Fermé"}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Zone de conversation */}
        <div style={{ flex: 2, border: "1px solid #ddd", borderRadius: 8, display: "flex", flexDirection: "column" }}>
          {selectedThread ? (
            <>
              {/* En-tête du thread */}
              <div style={{ padding: 16, borderBottom: "1px solid #eee", background: "#f9f9f9" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                  <div>
                    <h3 style={{ margin: 0, marginBottom: 4 }}>{selectedThread.subject}</h3>
                    <div style={{ fontSize: 12, color: "#666" }}>
                      Client: {selectedThread.user_id.slice(-8)}
                      {selectedThread.order_id && ` • Commande #${selectedThread.order_id.slice(-8)}`}
                      {selectedThread.closed && " • 🔒 Fermé"}
                    </div>
                  </div>
                  {!selectedThread.closed && (
                    <button
                      onClick={() => closeThread(selectedThread.id)}
                      style={{
                        background: "#dc3545",
                        color: "white",
                        border: "none",
                        padding: "6px 12px",
                        borderRadius: 4,
                        cursor: "pointer",
                        fontSize: 12,
                      }}
                    >
                      Fermer le fil
                    </button>
                  )}
                </div>
              </div>

              {/* Messages */}
              <div style={{ flex: 1, padding: 16, overflowY: "auto", maxHeight: 400 }}>
                {selectedThread.messages.length === 0 ? (
                  <p style={{ color: "#666", textAlign: "center" }}>
                    Aucun message dans cette conversation
                  </p>
                ) : (
                  <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                    {selectedThread.messages.map((message) => (
                      <div
                        key={message.id}
                        style={{
                          display: "flex",
                          flexDirection: "column",
                          alignItems: message.author_user_id ? "flex-start" : "flex-end",
                        }}
                      >
                        <div
                          style={{
                            maxWidth: "70%",
                            padding: 12,
                            borderRadius: 12,
                            background: message.author_user_id ? "#f1f1f1" : "#007bff",
                            color: message.author_user_id ? "black" : "white",
                          }}
                        >
                          <div style={{ marginBottom: 4 }}>{message.content}</div>
                          <div style={{ fontSize: 10, opacity: 0.7 }}>
                            {message.author_name} • {formatDate(message.created_at)}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Formulaire d'envoi de message */}
              {!selectedThread.closed && (
                <form onSubmit={sendMessage} style={{ padding: 16, borderTop: "1px solid #eee" }}>
                  <div style={{ display: "flex", gap: 8 }}>
                    <input
                      type="text"
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                      placeholder="Réponse du support..."
                      style={{
                        flex: 1,
                        padding: 8,
                        border: "1px solid #ddd",
                        borderRadius: 4,
                      }}
                    />
                    <button
                      type="submit"
                      disabled={!newMessage.trim()}
                      style={{
                        background: "#007bff",
                        color: "white",
                        border: "none",
                        padding: "8px 16px",
                        borderRadius: 4,
                        cursor: "pointer",
                        opacity: newMessage.trim() ? 1 : 0.5,
                      }}
                    >
                      Envoyer
                    </button>
                  </div>
                </form>
              )}

              {selectedThread.closed && (
                <div style={{ padding: 16, textAlign: "center", color: "#666", background: "#f9f9f9" }}>
                  🔒 Cette conversation est fermée
                </div>
              )}
            </>
          ) : (
            <div style={{ 
              display: "flex", 
              alignItems: "center", 
              justifyContent: "center", 
              height: "100%",
              color: "#666" 
            }}>
              Sélectionnez une conversation
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
