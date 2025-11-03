import React, { useEffect, useState } from "react";
// Page listant les commandes de l'utilisateur avec actions (annuler, facture).
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { useAuth } from "../hooks/useAuth";

export default function Orders() {
  const { isAuthenticated } = useAuth();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [downloadingInvoice, setDownloadingInvoice] = useState(null); // Track which invoice is being downloaded

  useEffect(() => {
    if (!isAuthenticated()) {
      setLoading(false);
      return;
    }

    async function fetchOrders() {
      try {
        setError(""); // Réinitialiser les erreurs
        setLoading(true);
        
        // Petit délai pour s'assurer que l'authentification est complète
        await new Promise(resolve => setTimeout(resolve, 100));
        
        const data = await api.myOrders();
        setOrders(data);
      } catch (err) {
        console.error("Erreur chargement commandes:", err);
        setError(`Erreur lors du chargement de vos commandes: ${err.message}`);
      } finally {
        setLoading(false);
      }
    }

    fetchOrders();
  }, [isAuthenticated]);

  const fmt = new Intl.NumberFormat("fr-FR", {
    style: "currency",
    currency: "EUR",
  });

  const getStatusColor = (status) => {
    switch (status) {
      case "CREE": return "#6b7280";      // Gris - En attente
      case "VALIDEE": return "#f59e0b";   // Orange - Validée
      case "PAYEE": return "#059669";     // Vert - Payée
      case "EXPEDIEE": return "#2563eb";  // Bleu - Expédiée
      case "LIVREE": return "#7c3aed";    // Violet - Livrée
      case "ANNULEE": return "#dc2626";   // Rouge - Annulée
      case "REMBOURSEE": return "#8b5cf6"; // Violet foncé - Remboursée
      default: return "#6b7280";
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case "CREE": return "Créée";
      case "VALIDEE": return "Validée";
      case "PAYEE": return "Payée";
      case "EXPEDIEE": return "Expédiée";
      case "LIVREE": return "Livrée";
      case "ANNULEE": return "Annulée";
      case "REMBOURSEE": return "Remboursée";
      default: return status;
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case "CREE": return "";
      case "VALIDEE": return "";
      case "PAYEE": return "";
      case "EXPEDIEE": return "";
      case "LIVREE": return "";
      case "ANNULEE": return "";
      case "REMBOURSEE": return "";
      default: return "";
    }
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp * 1000).toLocaleDateString("fr-FR", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    });
  };

  if (!isAuthenticated()) {
    return (
      <div style={{ padding: 40 }}>
        <h2>Mes commandes</h2>
        <div style={{
          padding: 24,
          backgroundColor: "#fef3c7",
          border: "1px solid #f59e0b",
          borderRadius: 8,
          textAlign: "center"
        }}>
          <p style={{ margin: 0, color: "#92400e" }}>
            Vous devez être connecté pour voir vos commandes.
          </p>
          <Link 
            to="/login" 
            style={{ 
              display: "inline-block", 
              marginTop: 12, 
              color: "#2563eb",
              textDecoration: "none",
              fontWeight: 600
            }}
          >
            Se connecter
          </Link>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div style={{ padding: 40 }}>
        <h2>Mes commandes</h2>
        <p>Chargement de vos commandes...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: 40 }}>
        <h2>Mes commandes</h2>
        <div style={{
          padding: 16,
          backgroundColor: "#fef2f2",
          border: "1px solid #fecaca",
          borderRadius: 8,
          color: "#dc2626"
        }}>
          {error}
        </div>
      </div>
    );
  }

  return (
    <>
      <style>
        {`
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `}
      </style>
      <div style={{ padding: 40 }}>
        <h2>Mes commandes</h2>
      
      {orders.length === 0 ? (
        <div style={{
          padding: 48,
          textAlign: "center",
          color: "#6b7280"
        }}>
          <p>Vous n'avez pas encore de commandes.</p>
          <Link 
            to="/" 
            style={{ 
              color: "#2563eb",
              textDecoration: "none",
              fontWeight: 600
            }}
          >
            Découvrir nos produits
          </Link>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {orders.map((order) => (
            <div
              key={order.id}
              style={{
                border: "1px solid #e5e7eb",
                borderRadius: 12,
                padding: 20,
                backgroundColor: "white"
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12 }}>
                <div>
                  <h3 style={{ margin: 0, fontSize: 18 }}>
                    Commande #{order.id.slice(-8)}
                  </h3>
                  <p style={{ margin: "4px 0 0 0", color: "#6b7280", fontSize: 14 }}>
                    {order.created_at ? formatDate(order.created_at) : ""}
                  </p>
                </div>
                <div style={{ textAlign: "right" }}>
                  <div style={{
                    padding: "6px 12px",
                    backgroundColor: getStatusColor(order.status) + "20",
                    color: getStatusColor(order.status),
                    borderRadius: 20,
                    fontSize: 12,
                    fontWeight: 600,
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "6px",
                    border: `1px solid ${getStatusColor(order.status)}30`
                  }}>
                    <span>{getStatusIcon(order.status)}</span>
                    {getStatusLabel(order.status)}
                  </div>
                  <div style={{ marginTop: 8, fontSize: 18, fontWeight: 700 }}>
                    {fmt.format(order.total_cents / 100)}
                  </div>
                </div>
              </div>

              <div style={{ marginBottom: 16 }}>
                <p style={{ margin: 0, color: "#374151", fontSize: 14 }}>
                  {order.items.length} article{order.items.length > 1 ? "s" : ""}
                </p>
                {order.items.slice(0, 2).map((item, index) => (
                  <p key={index} style={{ margin: "2px 0", color: "#6b7280", fontSize: 13 }}>
                    {item.name} × {item.quantity}
                  </p>
                ))}
                {order.items.length > 2 && (
                  <p style={{ margin: "2px 0", color: "#6b7280", fontSize: 13 }}>
                    ... et {order.items.length - 2} autre{order.items.length - 2 > 1 ? "s" : ""}
                  </p>
                )}
                
                {/* Informations de livraison */}
                {order.delivery && (
                  <div style={{ 
                    marginTop: 8, 
                    padding: "8px 12px", 
                    backgroundColor: "#f9fafb", 
                    borderRadius: 6,
                    border: "1px solid #e5e7eb"
                  }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <span style={{ color: "#6b7280", fontSize: 12 }}>
                        {order.delivery.transporteur}
                        {order.delivery.tracking_number && ` • ${order.delivery.tracking_number}`}
                      </span>
                      <div style={{
                        padding: "2px 6px",
                        backgroundColor: order.delivery.delivery_status === "LIVRÉE" ? "#dcfce7" : 
                                       order.delivery.delivery_status === "EN_COURS" ? "#dbeafe" : "#fef3c7",
                        color: order.delivery.delivery_status === "LIVRÉE" ? "#166534" : 
                               order.delivery.delivery_status === "EN_COURS" ? "#1e40af" : "#92400e",
                        borderRadius: 8,
                        fontSize: 10,
                        fontWeight: 600
                      }}>
                        {order.delivery.delivery_status}
                      </div>
                    </div>
                  </div>
                )}
              </div>

              <div style={{ display: "flex", gap: 12, flexWrap: "wrap", alignItems: "stretch" }}>
                <Link
                  to={`/orders/${order.id}`}
                  style={{
                    padding: "10px 20px",
                    backgroundColor: "#f3f4f6",
                    color: "#374151",
                    textDecoration: "none",
                    borderRadius: 8,
                    fontSize: 14,
                    fontWeight: 600,
                    display: "inline-flex",
                    alignItems: "center",
                    gap: 8,
                    border: "2px solid #e5e7eb",
                    transition: "all 0.2s"
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.backgroundColor = "#e5e7eb";
                    e.target.style.transform = "translateY(-1px)";
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.backgroundColor = "#f3f4f6";
                    e.target.style.transform = "translateY(0)";
                  }}
                >
                  Voir le détail
                </Link>
                
                {order.status === "PAYEE" && (
                  <button
                    onClick={async () => {
                      setDownloadingInvoice(order.id);
                      try {
                        await api.downloadInvoicePDF(order.id);
                        // Success feedback - could add a toast notification here
                      } catch (err) {
                        alert("Erreur lors du téléchargement de la facture : " + (err.message || "Erreur inconnue"));
                      } finally {
                        setDownloadingInvoice(null);
                      }
                    }}
                    disabled={downloadingInvoice === order.id}
                    style={{
                      padding: "10px 20px",
                      backgroundColor: downloadingInvoice === order.id ? "#93c5fd" : "#3b82f6",
                      color: "white",
                      border: "2px solid #2563eb",
                      borderRadius: 8,
                      fontSize: 14,
                      fontWeight: 600,
                      cursor: downloadingInvoice === order.id ? "wait" : "pointer",
                      display: "inline-flex",
                      alignItems: "center",
                      gap: 8,
                      transition: "all 0.2s",
                      opacity: downloadingInvoice === order.id ? 0.7 : 1,
                      boxShadow: downloadingInvoice === order.id ? "none" : "0 2px 4px rgba(59, 130, 246, 0.3)"
                    }}
                    onMouseEnter={(e) => {
                      if (downloadingInvoice !== order.id) {
                        e.target.style.backgroundColor = "#2563eb";
                        e.target.style.transform = "translateY(-1px)";
                        e.target.style.boxShadow = "0 4px 6px rgba(59, 130, 246, 0.4)";
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (downloadingInvoice !== order.id) {
                        e.target.style.backgroundColor = "#3b82f6";
                        e.target.style.transform = "translateY(0)";
                        e.target.style.boxShadow = "0 2px 4px rgba(59, 130, 246, 0.3)";
                      }
                    }}
                  >
                    {downloadingInvoice === order.id ? (
                      <>
                        <span>Téléchargement...</span>
                      </>
                    ) : (
                      <>
                        <span>Télécharger la facture</span>
                      </>
                    )}
                  </button>
                )}

                {["CREE", "VALIDEE", "PAYEE"].includes(order.status) && (
                  <button
                    onClick={async () => {
                      if (confirm("Êtes-vous sûr de vouloir annuler cette commande ?")) {
                        try {
                          await api.cancelOrder(order.id);
                          // Recharger les commandes
                          const updatedOrders = await api.myOrders();
                          setOrders(updatedOrders);
                        } catch (err) {
                          alert("Erreur lors de l'annulation : " + (err.message || "Erreur inconnue"));
                        }
                      }
                    }}
                    style={{
                      padding: "10px 20px",
                      backgroundColor: "#fef2f2",
                      color: "#dc2626",
                      border: "2px solid #fecaca",
                      borderRadius: 8,
                      fontSize: 14,
                      fontWeight: 600,
                      cursor: "pointer",
                      display: "inline-flex",
                      alignItems: "center",
                      gap: 8,
                      transition: "all 0.2s"
                    }}
                    onMouseEnter={(e) => {
                      e.target.style.backgroundColor = "#fee2e2";
                      e.target.style.transform = "translateY(-1px)";
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.backgroundColor = "#fef2f2";
                      e.target.style.transform = "translateY(0)";
                    }}
                  >
                    Annuler
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
      </div>
    </>
  );
}
