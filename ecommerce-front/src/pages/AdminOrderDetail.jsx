import React, { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { api } from "../lib/api";

export default function AdminOrderDetail() {
  const { orderId } = useParams();
  const navigate = useNavigate();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [msg, setMsg] = useState("");

  // Vérification admin
  const role = (typeof localStorage !== "undefined" && localStorage.getItem("role")) || "user";
  useEffect(() => {
    if (role !== "admin") {
      navigate("/", { replace: true });
    }
  }, [role, navigate]);

  useEffect(() => {
    async function fetchOrder() {
      try {
        const orderData = await api.adminGetOrder(orderId);
        setOrder(orderData);
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
  }, [orderId]);

  const fmt = new Intl.NumberFormat("fr-FR", {
    style: "currency",
    currency: "EUR",
  });

  const getStatusColor = (status) => {
    switch (status) {
      case "CREE": return "#6b7280";
      case "VALIDEE": return "#059669";
      case "PAYEE": return "#059669";
      case "EXPEDIEE": return "#2563eb";
      case "LIVREE": return "#7c3aed";
      case "ANNULEE": return "#dc2626";
      case "REMBOURSEE": return "#dc2626";
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

  const handleValidate = async () => {
    try {
      await api.adminValidateOrder(orderId);
      setMsg("✅ Commande validée");
      // Recharger la commande
      const updatedOrder = await api.adminGetOrder(orderId);
      setOrder(updatedOrder);
    } catch (err) {
      setError(err.message || "Erreur lors de la validation");
    }
  };

  const handleShip = async () => {
    try {
      await api.adminShipOrder(orderId);
      setMsg("✅ Commande expédiée");
      // Recharger la commande
      const updatedOrder = await api.adminGetOrder(orderId);
      setOrder(updatedOrder);
    } catch (err) {
      setError(err.message || "Erreur lors de l'expédition");
    }
  };

  const handleMarkDelivered = async () => {
    try {
      await api.adminMarkDelivered(orderId);
      setMsg("✅ Commande marquée comme livrée");
      // Recharger la commande
      const updatedOrder = await api.adminGetOrder(orderId);
      setOrder(updatedOrder);
    } catch (err) {
      setError(err.message || "Erreur lors de la mise à jour");
    }
  };

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
        <Link to="/admin" style={{ color: "#2563eb", textDecoration: "none" }}>
          ← Retour à l'admin
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
          to="/admin" 
          style={{ 
            color: "#2563eb", 
            textDecoration: "none",
            fontSize: 14,
            fontWeight: 600
          }}
        >
          ← Retour à l'admin
        </Link>
      </div>

      {/* Messages */}
      {msg && (
        <div style={{
          padding: "10px 12px", borderRadius: 8, marginBottom: 12,
          background: "#ecfdf5", color: "#065f46", border: "1px solid #a7f3d0", fontWeight: 600
        }}>
          {msg}
        </div>
      )}

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 32 }}>
        <div>
          <h1 style={{ margin: 0, fontSize: 32, fontWeight: 700 }}>
            Commande #{order.id.slice(-8)}
          </h1>
          <p style={{ margin: "8px 0 0 0", color: "#6b7280" }}>
            Client: {order.user_id}
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

          {/* Informations de livraison */}
          {order.delivery && (
            <div style={{ marginTop: 24 }}>
              <h3 style={{ marginBottom: 16 }}>Informations de livraison</h3>
              <div style={{
                padding: 16,
                border: "1px solid #e5e7eb",
                borderRadius: 8,
                backgroundColor: "white"
              }}>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                  <div>
                    <strong>Transporteur:</strong> {order.delivery.transporteur}
                  </div>
                  <div>
                    <strong>Statut:</strong> {order.delivery.delivery_status}
                  </div>
                  {order.delivery.tracking_number && (
                    <div style={{ gridColumn: "1 / -1" }}>
                      <strong>Numéro de suivi:</strong> {order.delivery.tracking_number}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Actions Admin */}
        <div>
          <h3 style={{ marginBottom: 16 }}>Actions</h3>
          <div style={{
            padding: 20,
            border: "1px solid #e5e7eb",
            borderRadius: 8,
            backgroundColor: "white"
          }}>
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {order.status === "PAYEE" && (
                <button
                  onClick={handleValidate}
                  style={{
                    padding: "12px 16px",
                    backgroundColor: "#059669",
                    color: "white",
                    border: "none",
                    borderRadius: 8,
                    cursor: "pointer",
                    fontWeight: 600
                  }}
                >
                  ✅ Valider la commande
                </button>
              )}

              {order.status === "VALIDEE" && (
                <button
                  onClick={handleShip}
                  style={{
                    padding: "12px 16px",
                    backgroundColor: "#2563eb",
                    color: "white",
                    border: "none",
                    borderRadius: 8,
                    cursor: "pointer",
                    fontWeight: 600
                  }}
                >
                  🚚 Expédier la commande
                </button>
              )}

              {order.status === "EXPEDIEE" && (
                <button
                  onClick={handleMarkDelivered}
                  style={{
                    padding: "12px 16px",
                    backgroundColor: "#7c3aed",
                    color: "white",
                    border: "none",
                    borderRadius: 8,
                    cursor: "pointer",
                    fontWeight: 600
                  }}
                >
                  📦 Marquer comme livrée
                </button>
              )}

              <div style={{ fontSize: 14, color: "#6b7280", textAlign: "center", marginTop: 8 }}>
                Statut actuel: <strong>{getStatusLabel(order.status)}</strong>
              </div>
            </div>
          </div>

          {/* Résumé */}
          <div style={{ marginTop: 20 }}>
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
          </div>
        </div>
      </div>
    </div>
  );
}
