import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api } from "../lib/api";
import { useAuth } from "../contexts/AuthContext";

export default function OrderDetail() {
  const { orderId } = useParams();
  const { isAuthenticated } = useAuth();
  const [order, setOrder] = useState(null);
  const [invoice, setInvoice] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!isAuthenticated()) {
      setLoading(false);
      return;
    }

    async function fetchOrder() {
      try {
        const orderData = await api.getOrder(orderId);
        setOrder(orderData);
        
        // Essayer de récupérer la facture si elle existe
        try {
          const invoiceData = await api.getInvoice(orderId);
          setInvoice(invoiceData);
        } catch (err) {
          // Pas de facture disponible
        }
      } catch (err) {
        console.error("Erreur chargement commande:", err);
        if (err.status === 404) {
          setError("Commande introuvable");
        } else {
          setError("Erreur lors du chargement de la commande");
        }
      } finally {
        setLoading(false);
      }
    }

    fetchOrder();
  }, [orderId, isAuthenticated]);

  const fmt = new Intl.NumberFormat("fr-FR", {
    style: "currency",
    currency: "EUR",
  });

  const getStatusColor = (status) => {
    switch (status) {
      case "CREE": return "#6b7280";
      case "PAYEE": return "#059669";
      case "EXPEDIEE": return "#2563eb";
      case "LIVREE": return "#7c3aed";
      case "ANNULEE": return "#dc2626";
      default: return "#6b7280";
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case "CREE": return "En attente de paiement";
      case "PAYEE": return "Payée";
      case "EXPEDIEE": return "Expédiée";
      case "LIVREE": return "Livrée";
      case "ANNULEE": return "Annulée";
      default: return status;
    }
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp * 1000).toLocaleDateString("fr-FR", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    });
  };

  if (!isAuthenticated()) {
    return (
      <div style={{ padding: 40 }}>
        <h2>Détail de la commande</h2>
        <div style={{
          padding: 24,
          backgroundColor: "#fef3c7",
          border: "1px solid #f59e0b",
          borderRadius: 8,
          textAlign: "center"
        }}>
          <p style={{ margin: 0, color: "#92400e" }}>
            Vous devez être connecté pour voir les détails de cette commande.
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
        <h2>Détail de la commande</h2>
        <p>Chargement...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: 40 }}>
        <h2>Détail de la commande</h2>
        <div style={{
          padding: 16,
          backgroundColor: "#fef2f2",
          border: "1px solid #fecaca",
          borderRadius: 8,
          color: "#dc2626"
        }}>
          {error}
        </div>
        <Link to="/orders" style={{ color: "#2563eb", textDecoration: "none" }}>
          ← Retour à mes commandes
        </Link>
      </div>
    );
  }

  if (!order) {
    return (
      <div style={{ padding: 40 }}>
        <h2>Détail de la commande</h2>
        <p>Commande introuvable.</p>
      </div>
    );
  }

  return (
    <div style={{ padding: 40 }}>
      <div style={{ marginBottom: 24 }}>
        <Link 
          to="/orders" 
          style={{ 
            color: "#2563eb", 
            textDecoration: "none",
            fontSize: 14,
            fontWeight: 600
          }}
        >
          ← Retour à mes commandes
        </Link>
      </div>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 32 }}>
        <div>
          <h1 style={{ margin: 0, fontSize: 32, fontWeight: 700 }}>
            Commande #{order.id.slice(-8)}
          </h1>
          <p style={{ margin: "8px 0 0 0", color: "#6b7280" }}>
            Passée le {formatDate(Date.now() / 1000)} {/* Simulation */}
          </p>
        </div>
        <div style={{ textAlign: "right" }}>
          <div style={{
            padding: "8px 16px",
            backgroundColor: getStatusColor(order.status) + "20",
            color: getStatusColor(order.status),
            borderRadius: 20,
            fontSize: 14,
            fontWeight: 600,
            display: "inline-block",
            marginBottom: 8
          }}>
            {getStatusLabel(order.status)}
          </div>
          <div style={{ fontSize: 24, fontWeight: 700 }}>
            {fmt.format(order.total_cents / 100)}
          </div>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: 32, marginBottom: 32 }}>
        {/* Articles */}
        <div>
          <h3 style={{ marginBottom: 16 }}>Articles commandés</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {order.items.map((item, index) => (
              <div
                key={index}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  padding: 16,
                  border: "1px solid #e5e7eb",
                  borderRadius: 8,
                  backgroundColor: "white"
                }}
              >
                <div>
                  <h4 style={{ margin: 0, fontSize: 16, fontWeight: 600 }}>
                    {item.name}
                  </h4>
                  <p style={{ margin: "4px 0 0 0", color: "#6b7280", fontSize: 14 }}>
                    Quantité : {item.quantity}
                  </p>
                </div>
                <div style={{ textAlign: "right" }}>
                  <div style={{ fontSize: 16, fontWeight: 600 }}>
                    {fmt.format(item.unit_price_cents / 100)}
                  </div>
                  <div style={{ fontSize: 14, color: "#6b7280" }}>
                    × {item.quantity}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Résumé */}
        <div>
          <h3 style={{ marginBottom: 16 }}>Résumé</h3>
          <div style={{
            padding: 20,
            border: "1px solid #e5e7eb",
            borderRadius: 8,
            backgroundColor: "white"
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
              <span>Articles ({order.items.length})</span>
              <span>{fmt.format(order.total_cents / 100)}</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
              <span>Livraison</span>
              <span style={{ color: "#059669" }}>Gratuite</span>
            </div>
            <hr style={{ border: "none", borderTop: "1px solid #e5e7eb", margin: "12px 0" }} />
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 18, fontWeight: 700 }}>
              <span>Total</span>
              <span>{fmt.format(order.total_cents / 100)}</span>
            </div>
          </div>

          {/* Actions */}
          <div style={{ marginTop: 20, display: "flex", flexDirection: "column", gap: 12 }}>
            {invoice && (
              <Link
                to={`/orders/${order.id}/invoice`}
                style={{
                  padding: "12px 16px",
                  backgroundColor: "#dbeafe",
                  color: "#1d4ed8",
                  textDecoration: "none",
                  borderRadius: 8,
                  textAlign: "center",
                  fontWeight: 600
                }}
              >
                📄 Télécharger la facture
              </Link>
            )}

            {(order.status === "CREE" || order.status === "PAYEE") && order.status !== "EXPEDIEE" && (
              <button
                onClick={async () => {
                  if (confirm("Êtes-vous sûr de vouloir annuler cette commande ?")) {
                    try {
                      await api.cancelOrder(order.id);
                      // Recharger la commande
                      const updatedOrder = await api.getOrder(orderId);
                      setOrder(updatedOrder);
                    } catch (err) {
                      alert("Erreur lors de l'annulation : " + (err.message || "Erreur inconnue"));
                    }
                  }
                }}
                style={{
                  padding: "12px 16px",
                  backgroundColor: "#fef2f2",
                  color: "#dc2626",
                  border: "none",
                  borderRadius: 8,
                  cursor: "pointer",
                  fontWeight: 600
                }}
              >
                Annuler la commande
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
