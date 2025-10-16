// src/pages/Support.jsx
import React, { useState, useEffect } from "react";
import { api } from "../lib/api";
import { useAuth } from "../contexts/AuthContext";

export default function Support() {
  const { user, isAuthenticated } = useAuth();
  const [threads, setThreads] = useState([]);
  const [selectedThread, setSelectedThread] = useState(null);
  const [newMessage, setNewMessage] = useState("");
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Formulaire de création de thread
  const [newThread, setNewThread] = useState({
    subject: "",
    order_id: "",
  });

  // Charger les threads au montage
  useEffect(() => {
    if (isAuthenticated()) {
      loadThreads();
    }
  }, [isAuthenticated]);

  const loadThreads = async () => {
    try {
      setLoading(true);
      const data = await api.listSupportThreads();
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
      const data = await api.getSupportThread(threadId);
      setSelectedThread(data);
      
      // Marquer automatiquement les messages comme lus quand on ouvre le thread
      if (data.unread_count > 0) {
        try {
          await api.markSupportThreadAsRead(threadId);
          // Mettre à jour la liste des threads pour refléter le changement
          await loadThreads();
        } catch (markReadErr) {
          console.error("Erreur lors du marquage des messages comme lus:", markReadErr);
        }
      }
    } catch (err) {
      setError("Erreur lors du chargement du fil");
      console.error(err);
    }
  };

  const createThread = async (e) => {
    e.preventDefault();
    
    if (!isAuthenticated()) {
      setError("Vous devez être connecté pour créer un fil de support");
      return;
    }
    
    try {
      const data = await api.createSupportThread({
        subject: newThread.subject,
        order_id: newThread.order_id && newThread.order_id.trim() ? newThread.order_id.trim() : null,
      });
      setThreads([data, ...threads]);
      setNewThread({ subject: "", order_id: "" });
      setShowCreateForm(false);
      setError(null);
    } catch (err) {
      console.error("Erreur lors de la création du fil:", err);
      setError(`Erreur lors de la création du fil: ${err.message || err}`);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !selectedThread) return;

    try {
      const data = await api.postSupportMessage(selectedThread.id, {
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

  const formatDate = (timestamp) => {
    return new Date(timestamp * 1000).toLocaleString("fr-FR");
  };

  // Vérifier l'authentification
  if (!isAuthenticated()) {
    return (
      <div style={{ textAlign: "center", padding: 40 }}>
        <h2>Accès refusé</h2>
        <p>Vous devez être connecté pour accéder au support.</p>
      </div>
    );
  }

  if (loading) {
    return <div>Chargement des fils de discussion...</div>;
  }

  return (
    <div style={{ maxWidth: 1200, margin: "0 auto", padding: 20 }}>
      <h1>💬 Support Client</h1>
      
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
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
            <h2>Mes demandes</h2>
            <button
              onClick={() => setShowCreateForm(true)}
              style={{
                background: "#007bff",
                color: "white",
                border: "none",
                padding: "8px 16px",
                borderRadius: 4,
                cursor: "pointer",
              }}
            >
              + Nouvelle demande
            </button>
          </div>

          {threads.length === 0 ? (
            <p style={{ color: "#666", textAlign: "center", marginTop: 40 }}>
              Aucune demande de support
            </p>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {threads.map((thread) => (
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
                    position: "relative",
                  }}
                >
                  <div style={{ fontWeight: "bold", marginBottom: 4, display: "flex", alignItems: "center", gap: 8 }}>
                    {thread.subject}
                    {thread.unread_count > 0 && (
                      <span
                        style={{
                          background: "#dc2626",
                          color: "white",
                          borderRadius: "50%",
                          width: 20,
                          height: 20,
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          fontSize: 10,
                          fontWeight: "bold",
                        }}
                      >
                        {thread.unread_count}
                      </span>
                    )}
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
                <h3 style={{ margin: 0, marginBottom: 4 }}>{selectedThread.subject}</h3>
                <div style={{ fontSize: 12, color: "#666" }}>
                  {selectedThread.order_id ? `Commande #${selectedThread.order_id.slice(-8)}` : "Demande générale"}
                  {selectedThread.closed && " • 🔒 Fermé"}
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
                          alignItems: message.author_user_id ? "flex-end" : "flex-start",
                        }}
                      >
                        <div
                          style={{
                            maxWidth: "70%",
                            padding: 12,
                            borderRadius: 12,
                            background: message.author_user_id ? "#007bff" : "#f1f1f1",
                            color: message.author_user_id ? "white" : "black",
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
                      placeholder="Tapez votre message..."
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

      {/* Modal de création de thread */}
      {showCreateForm && (
        <div style={{
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: "rgba(0,0,0,0.5)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 1000,
        }}>
          <div style={{
            background: "white",
            padding: 24,
            borderRadius: 8,
            width: 400,
            maxWidth: "90vw",
          }}>
            <h3 style={{ marginTop: 0 }}>Nouvelle demande de support</h3>
            <form onSubmit={createThread}>
              <div style={{ marginBottom: 16 }}>
                <label style={{ display: "block", marginBottom: 4, fontWeight: "bold" }}>
                  Sujet *
                </label>
                <input
                  type="text"
                  value={newThread.subject}
                  onChange={(e) => setNewThread({ ...newThread, subject: e.target.value })}
                  placeholder="Décrivez votre problème..."
                  required
                  style={{
                    width: "100%",
                    padding: 8,
                    border: "1px solid #ddd",
                    borderRadius: 4,
                  }}
                />
              </div>
              <div style={{ marginBottom: 16 }}>
                <label style={{ display: "block", marginBottom: 4, fontWeight: "bold" }}>
                  Commande (optionnel)
                </label>
                <input
                  type="text"
                  value={newThread.order_id}
                  onChange={(e) => setNewThread({ ...newThread, order_id: e.target.value })}
                  placeholder="ID de la commande concernée..."
                  style={{
                    width: "100%",
                    padding: 8,
                    border: "1px solid #ddd",
                    borderRadius: 4,
                  }}
                />
              </div>
              <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  style={{
                    padding: "8px 16px",
                    border: "1px solid #ddd",
                    background: "white",
                    borderRadius: 4,
                    cursor: "pointer",
                  }}
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  style={{
                    padding: "8px 16px",
                    background: "#007bff",
                    color: "white",
                    border: "none",
                    borderRadius: 4,
                    cursor: "pointer",
                  }}
                >
                  Créer
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
