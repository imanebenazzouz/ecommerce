// src/pages/Support.jsx
//
// Support client: création de fils, lecture, réponses, marquage comme lu.
import React, { useState, useEffect } from "react";
import { api } from "../lib/api";
import { useAuth } from "../hooks/useAuth";

export default function Support() {
  const { isAuthenticated } = useAuth();
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

  // États pour l'autocomplétion des commandes
  const [userOrders, setUserOrders] = useState([]);
  const [showOrderSuggestions, setShowOrderSuggestions] = useState(false);
  const [filteredOrders, setFilteredOrders] = useState([]);
  const [orderValidation, setOrderValidation] = useState({ isValid: null, message: "" });

  // Charger les threads au montage
  useEffect(() => {
    if (isAuthenticated()) {
      loadThreads();
      loadUserOrders();
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

  const loadUserOrders = async () => {
    try {
      const orders = await api.myOrders();
      setUserOrders(orders);
    } catch (err) {
      console.error("Erreur lors du chargement des commandes:", err);
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
    
    // Validation de la commande si un ID est fourni
    if (newThread.order_id && newThread.order_id.trim()) {
      const orderExists = userOrders.find(order => order.id === newThread.order_id.trim());
      if (!orderExists) {
        setError("L'ID de commande saisi n'existe pas dans vos commandes. Veuillez utiliser l'autocomplétion ou laisser le champ vide.");
        return;
      }
    }
    
    try {
      const data = await api.createSupportThread({
        subject: newThread.subject,
        order_id: newThread.order_id && newThread.order_id.trim() ? newThread.order_id.trim() : null,
      });
      setThreads([data, ...threads]);
      setNewThread({ subject: "", order_id: "" });
      setShowCreateForm(false);
      setShowOrderSuggestions(false);
      setOrderValidation({ isValid: null, message: "" });
      setError(null);
    } catch (err) {
      console.error("Erreur lors de la création du fil:", err);
      setError(`Erreur lors de la création du fil: ${err.message || err}`);
    }
  };

  // Fonctions pour l'autocomplétion des commandes
  const handleOrderIdChange = (value) => {
    setNewThread({ ...newThread, order_id: value });
    
    // Réinitialiser la validation
    setOrderValidation({ isValid: null, message: "" });
    
    if (value.trim()) {
      const filtered = userOrders.filter(order => 
        order.id.toLowerCase().includes(value.toLowerCase()) ||
        order.id.slice(-8).includes(value)
      );
      setFilteredOrders(filtered);
      setShowOrderSuggestions(filtered.length > 0);
      
      // Vérifier si l'ID saisi correspond exactement à une commande
      const exactMatch = userOrders.find(order => order.id === value.trim());
      if (exactMatch) {
        setOrderValidation({ isValid: true, message: "Commande trouvée" });
      } else if (value.trim().length > 8) {
        // Si l'utilisateur a tapé quelque chose de long qui ne correspond à aucune commande
        setOrderValidation({ isValid: false, message: "Commande introuvable" });
      }
    } else {
      // Afficher toutes les commandes si le champ est vide
      setFilteredOrders(userOrders);
      setShowOrderSuggestions(userOrders.length > 0);
    }
  };

  const handleOrderIdFocus = () => {
    // Afficher toutes les commandes dès qu'on focus le champ
    if (userOrders.length > 0) {
      if (newThread.order_id.trim()) {
        handleOrderIdChange(newThread.order_id);
      } else {
        setFilteredOrders(userOrders);
        setShowOrderSuggestions(true);
      }
    }
  };

  const selectOrder = (orderId) => {
    setNewThread({ ...newThread, order_id: orderId });
    setShowOrderSuggestions(false);
    setFilteredOrders([]);
    setOrderValidation({ isValid: true, message: "Commande sélectionnée" });
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
    <div style={{ maxWidth: 1200, margin: "0 auto", padding: 20, paddingBottom: 120 }}>
      <h1>Support Client</h1>
      
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

      <div style={{ display: "flex", gap: 20, height: "70vh", minHeight: 0 }}>
        {/* Liste des threads */}
        <div style={{ flex: 1, border: "1px solid #ddd", borderRadius: 8, padding: 16, overflowY: "auto" }}>
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
        <div style={{ flex: 2, border: "1px solid #ddd", borderRadius: 8, display: "flex", flexDirection: "column", minHeight: 0 }}>
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
              <div style={{ flex: 1, padding: 16, overflowY: "auto" }}>
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
              <div style={{ marginBottom: 16, position: "relative" }}>
                <label style={{ display: "block", marginBottom: 4, fontWeight: "bold" }}>
                  Commande (optionnel)
                </label>
                <div style={{ position: "relative" }}>
                  <input
                    type="text"
                    value={newThread.order_id}
                    onChange={(e) => handleOrderIdChange(e.target.value)}
                    onFocus={handleOrderIdFocus}
                    onBlur={() => {
                      // Délai pour permettre le clic sur une suggestion
                      setTimeout(() => setShowOrderSuggestions(false), 200);
                    }}
                    placeholder="Cliquez pour voir vos commandes..."
                    style={{
                      width: "100%",
                      padding: 8,
                      border: orderValidation.isValid === false ? "1px solid #dc3545" : 
                              orderValidation.isValid === true ? "1px solid #28a745" : "1px solid #ddd",
                      borderRadius: 4,
                    }}
                  />
                  {showOrderSuggestions && filteredOrders.length > 0 && (
                    <div style={{
                      position: "absolute",
                      top: "100%",
                      left: 0,
                      right: 0,
                      background: "white",
                      border: "1px solid #ddd",
                      borderTop: "none",
                      borderRadius: "0 0 4px 4px",
                      maxHeight: 200,
                      overflowY: "auto",
                      zIndex: 1000,
                      boxShadow: "0 2px 8px rgba(0,0,0,0.1)"
                    }}>
                      <div style={{
                        padding: "6px 12px",
                        background: "#f8f9fa",
                        fontSize: 11,
                        color: "#666",
                        fontWeight: "bold",
                        borderBottom: "1px solid #e0e0e0"
                      }}>
                        {filteredOrders.length === userOrders.length 
                          ? `${userOrders.length} commande(s) disponible(s)` 
                          : `${filteredOrders.length} résultat(s) trouvé(s)`}
                      </div>
                      {filteredOrders.slice(0, 5).map((order) => (
                        <div
                          key={order.id}
                          onClick={() => selectOrder(order.id)}
                          style={{
                            padding: "8px 12px",
                            cursor: "pointer",
                            borderBottom: "1px solid #f0f0f0",
                            fontSize: 12,
                          }}
                          onMouseEnter={(e) => {
                            e.currentTarget.style.background = "#f8f9fa";
                          }}
                          onMouseLeave={(e) => {
                            e.currentTarget.style.background = "white";
                          }}
                        >
                          <div style={{ fontWeight: "bold", color: "#007bff" }}>
                            Commande #{order.id.slice(-8)}
                          </div>
                          <div style={{ color: "#666", fontSize: 11 }}>
                            {order.status} • {new Date(order.created_at * 1000).toLocaleDateString("fr-FR")}
                          </div>
                        </div>
                      ))}
                      {filteredOrders.length > 5 && (
                        <div style={{
                          padding: "6px 12px",
                          fontSize: 11,
                          color: "#999",
                          textAlign: "center",
                          background: "#fafafa"
                        }}>
                          +{filteredOrders.length - 5} autre(s) commande(s)
                        </div>
                      )}
                    </div>
                  )}
                </div>
                {orderValidation.message && (
                  <div style={{ 
                    fontSize: 11, 
                    color: orderValidation.isValid ? "#28a745" : "#dc3545", 
                    marginTop: 4,
                    fontWeight: "bold"
                  }}>
                    {orderValidation.message}
                  </div>
                )}
                {!orderValidation.message && userOrders.length > 0 && (
                  <div style={{ fontSize: 11, color: "#666", marginTop: 4 }}>
                    {userOrders.length} commande(s) disponible(s) - Cliquez ou tapez pour rechercher
                  </div>
                )}
                {!orderValidation.message && userOrders.length === 0 && (
                  <div style={{ fontSize: 11, color: "#999", marginTop: 4 }}>
                    Aucune commande disponible. Passez d'abord une commande pour la lier au support.
                  </div>
                )}
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
