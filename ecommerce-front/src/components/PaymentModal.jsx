import React, { useState } from "react";
import { api } from "../lib/api";

export default function PaymentModal({ 
  orderId, 
  amountCents, 
  onSuccess, 
  onCancel, 
  isOpen 
}) {
  const [cardNumber, setCardNumber] = useState("");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  if (!isOpen) return null;

  const fmt = new Intl.NumberFormat("fr-FR", {
    style: "currency",
    currency: "EUR",
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!cardNumber.trim()) {
      setError("Numéro de carte requis");
      return;
    }

    setPending(true);
    setError("");

    try {
      const result = await api.processPayment({
        orderId,
        cardNumber: cardNumber.replace(/\D/g, ""),
        expMonth: 12,
        expYear: 2025,
        cvc: "123"
      });

      if (result.status === "SUCCEEDED") {
        setSuccess(true);
        setTimeout(() => {
          onSuccess(result);
        }, 2000);
      } else {
        setError("Paiement refusé. Vérifiez votre carte bancaire.");
      }
    } catch (err) {
      console.error("Erreur paiement:", err);
      let errorMessage = "Erreur lors du paiement. Veuillez réessayer.";
      
      if (err.status === 402) {
        errorMessage = "Paiement refusé. Vérifiez votre carte bancaire.";
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
    } finally {
      setPending(false);
    }
  };

  const handleCardNumberChange = (e) => {
    const value = e.target.value.replace(/\D/g, ""); // Garder seulement les chiffres
    setCardNumber(value);
  };

  return (
    <div style={{
      position: "fixed",
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: "rgba(0, 0, 0, 0.5)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      zIndex: 1000
    }}>
      <div style={{
        backgroundColor: "white",
        padding: 32,
        borderRadius: 12,
        maxWidth: 500,
        width: "90%",
        maxHeight: "90vh",
        overflow: "auto"
      }}>
        {success ? (
          <div style={{ textAlign: "center" }}>
            <div style={{ fontSize: 48, marginBottom: 16 }}>✅</div>
            <h2 style={{ color: "#059669", marginBottom: 16 }}>
              Paiement réussi !
            </h2>
            <p style={{ color: "#374151", marginBottom: 24 }}>
              Votre commande a été payée avec succès.
            </p>
            <p style={{ fontSize: 14, color: "#6b7280" }}>
              Redirection vers vos commandes...
            </p>
          </div>
        ) : (
          <>
            <h2 style={{ marginBottom: 8 }}>Paiement</h2>
            <p style={{ color: "#6b7280", marginBottom: 24 }}>
              Total à payer : <strong>{fmt.format(amountCents / 100)}</strong>
            </p>

            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: 16 }}>
                <label style={{ display: "block", marginBottom: 8, fontWeight: 600 }}>
                  Numéro de carte
                </label>
                <input
                  type="text"
                  value={cardNumber}
                  onChange={handleCardNumberChange}
                  placeholder="4242424242424242"
                  maxLength={19}
                  style={{
                    width: "100%",
                    padding: 12,
                    border: "1px solid #d1d5db",
                    borderRadius: 8,
                    fontSize: 16
                  }}
                />
                <p style={{ fontSize: 12, color: "#6b7280", marginTop: 4 }}>
                  💡 Pour tester : utilisez 4242... (accepté) ou ...0000 (refusé)
                </p>
              </div>

              {error && (
                <div style={{
                  padding: 12,
                  backgroundColor: "#fef2f2",
                  border: "1px solid #fecaca",
                  borderRadius: 8,
                  color: "#dc2626",
                  marginBottom: 16
                }}>
                  {error}
                </div>
              )}

              <div style={{ display: "flex", gap: 12, justifyContent: "flex-end" }}>
                <button
                  type="button"
                  onClick={onCancel}
                  disabled={pending}
                  style={{
                    padding: "12px 24px",
                    backgroundColor: "#f3f4f6",
                    color: "#374151",
                    border: "none",
                    borderRadius: 8,
                    cursor: "pointer",
                    fontWeight: 600
                  }}
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  disabled={pending || !cardNumber.trim()}
                  style={{
                    padding: "12px 24px",
                    backgroundColor: pending ? "#9ca3af" : "#2563eb",
                    color: "white",
                    border: "none",
                    borderRadius: 8,
                    cursor: pending ? "not-allowed" : "pointer",
                    fontWeight: 600
                  }}
                >
                  {pending ? "Traitement..." : `Payer ${fmt.format(amountCents / 100)}`}
                </button>
              </div>
            </form>
          </>
        )}
      </div>
    </div>
  );
}
