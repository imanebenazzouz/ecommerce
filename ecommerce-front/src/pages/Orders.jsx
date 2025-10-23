import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { useAuth } from "../hooks/useAuth";

export default function Orders() {
  const { isAuthenticated } = useAuth();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

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
      case "CREE": return "📋";
      case "VALIDEE": return "✅";
      case "PAYEE": return "💳";
      case "EXPEDIEE": return "🚚";
      case "LIVREE": return "📦";
      case "ANNULEE": return "❌";
      case "REMBOURSEE": return "💰";
      default: return "📋";
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
    <div style={{ padding: 40 }}>
      <h2>Mes commandes</h2>
      
      {orders.length === 0 ? (
        <div style={{
          padding: 48,
          textAlign: "center",
          color: "#6b7280"
        }}>
          <div style={{ fontSize: 48, marginBottom: 16 }}>📦</div>
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
                    {formatDate(Date.now() / 1000)} {/* Simulation - en réalité utiliser order.created_at */}
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
                        📦 {order.delivery.transporteur}
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

              <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
                <Link
                  to={`/orders/${order.id}`}
                  style={{
                    padding: "8px 16px",
                    backgroundColor: "#f3f4f6",
                    color: "#374151",
                    textDecoration: "none",
                    borderRadius: 6,
                    fontSize: 14,
                    fontWeight: 600
                  }}
                >
                  Voir le détail
                </Link>
                
                {order.status === "PAYEE" && (
                  <button
                    onClick={async () => {
                      try {
                        await api.downloadInvoicePDF(order.id);
                      } catch (err) {
                        alert("Erreur lors du téléchargement : " + (err.message || "Erreur inconnue"));
                      }
                    }}
                    style={{
                      padding: "8px 16px",
                      backgroundColor: "#dbeafe",
                      color: "#1d4ed8",
                      border: "none",
                      borderRadius: 6,
                      fontSize: 14,
                      fontWeight: 600,
                      cursor: "pointer"
                    }}
                  >
                    📄 Facture PDF
                  </button>
                )}

                {(order.status === "CREE" || order.status === "PAYEE") && order.status !== "EXPEDIEE" && (
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
                      padding: "8px 16px",
                      backgroundColor: "#fef2f2",
                      color: "#dc2626",
                      border: "none",
                      borderRadius: 6,
                      fontSize: 14,
                      fontWeight: 600,
                      cursor: "pointer"
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
  );
}
