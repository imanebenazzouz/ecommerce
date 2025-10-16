// src/pages/Cart.jsx
import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import { useAuth } from "../contexts/AuthContext";
import PaymentModal from "../components/PaymentModal";

export default function Cart() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [cart, setCart] = useState(null);
  const [products, setProducts] = useState([]);
  const [orderId, setOrderId] = useState(null);
  const [err, setErr] = useState("");
  const [msg, setMsg] = useState("");
  const [pending, setPending] = useState(false);
  const [showPaymentModal, setShowPaymentModal] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const ps = await api.listProducts();
        setProducts(ps);

        if (isAuthenticated()) {
          // Utilisateur connecté : récupérer le panier du serveur
          const c = await api.getCart();
          setCart(c);
        } else {
          // Utilisateur non connecté : récupérer le panier local
          const localCart = getLocalCart();
          setCart(localCart);
        }
      } catch (e) {
        setErr(e.message);
        if (e.status === 401) {
          // En cas d'erreur 401, basculer sur le panier local
          const localCart = getLocalCart();
          setCart(localCart);
        }
      }
    })();
  }, [isAuthenticated]);

  // Fonction pour récupérer le panier local
  function getLocalCart() {
    const localCartData = localStorage.getItem('localCart');
    return localCartData ? JSON.parse(localCartData) : { items: {} };
  }

  // Fonction pour sauvegarder le panier local
  function saveLocalCart(cartData) {
    localStorage.setItem('localCart', JSON.stringify(cartData));
  }

  // Maps utiles
  const priceById = useMemo(() => {
    const m = new Map();
    products.forEach((p) => m.set(p.id, p.price_cents));
    return m;
  }, [products]);

  const nameById = useMemo(() => {
    const m = new Map();
    products.forEach((p) => m.set(p.id, p.name));
    return m;
  }, [products]);

  const fmt = new Intl.NumberFormat("fr-FR", { style: "currency", currency: "EUR" });

  const items = useMemo(() => Object.values(cart?.items || {}), [cart]);

  const totalCents = useMemo(() => {
    if (!cart) return 0;
    return items.reduce((sum, it) => {
      const unit = priceById.get(it.product_id) || 0;
      return sum + unit * it.quantity;
    }, 0);
  }, [items, priceById, cart]);

  async function reload() {
    try {
      if (isAuthenticated()) {
        const c = await api.getCart();
        setCart(c);
      } else {
        const localCart = getLocalCart();
        setCart(localCart);
      }
    } catch (e) {
      setErr(e.message);
    }
  }

  // --- Actions ligne ---
  async function inc(product_id) {
    setErr(""); setMsg(""); setPending(true);
    try {
      if (isAuthenticated()) {
        await api.addToCart({ product_id, qty: 1 });
        await reload();
      } else {
        // Gestion du panier local
        const localCart = getLocalCart();
        const existingItem = localCart.items[product_id];
        if (existingItem) {
          localCart.items[product_id].quantity += 1;
        } else {
          localCart.items[product_id] = { product_id, quantity: 1 };
        }
        saveLocalCart(localCart);
        setCart(localCart);
      }
    } catch (e) {
      setErr(e.message);
    } finally {
      setPending(false);
    }
  }

  async function dec(product_id) {
    setErr(""); setMsg(""); setPending(true);
    try {
      if (isAuthenticated()) {
        await api.removeFromCart({ product_id, qty: 1 });
        await reload();
      } else {
        // Gestion du panier local
        const localCart = getLocalCart();
        const existingItem = localCart.items[product_id];
        if (existingItem && existingItem.quantity > 1) {
          localCart.items[product_id].quantity -= 1;
          saveLocalCart(localCart);
          setCart(localCart);
        }
      }
    } catch (e) {
      setErr(e.message);
    } finally {
      setPending(false);
    }
  }

  async function removeAll(product_id) {
    setErr(""); setMsg(""); setPending(true);
    try {
      if (isAuthenticated()) {
        // qty: 0 = supprimer l'article entièrement (supporté par ton API)
        await api.removeFromCart({ product_id, qty: 0 });
        await reload();
      } else {
        // Gestion du panier local
        const localCart = getLocalCart();
        delete localCart.items[product_id];
        saveLocalCart(localCart);
        setCart(localCart);
      }
    } catch (e) {
      setErr(e.message);
    } finally {
      setPending(false);
    }
  }

  // --- Actions globales ---
  async function clearCart() {
    if (items.length === 0) return;
    setErr(""); setMsg(""); setPending(true);
    try {
      if (isAuthenticated()) {
        // supprime chaque article (qty=0) en parallèle
        await Promise.all(items.map(it => api.removeFromCart({ product_id: it.product_id, qty: 0 })));
        await reload();
      } else {
        // Gestion du panier local
        const emptyCart = { items: {} };
        saveLocalCart(emptyCart);
        setCart(emptyCart);
      }
    } catch (e) {
      setErr(e.message);
    } finally {
      setPending(false);
    }
  }

  async function checkout() {
    setErr(""); setMsg("");
    
    // Vérification d'authentification avant le paiement
    if (!isAuthenticated()) {
      // Redirection vers login avec paramètre de retour
      navigate("/login?next=/cart");
      return;
    }

    setPending(true);
    try {
      const res = await api.checkout();
      setOrderId(res.order_id);
      setShowPaymentModal(true);
      setMsg("Commande créée avec succès !");
    } catch (e) {
      setErr(e.message);
    } finally {
      setPending(false);
    }
  }

  const handlePaymentSuccess = (paymentResult) => {
    setShowPaymentModal(false);
    setMsg("✅ Paiement réussi ! Redirection vers vos commandes...");
    
    // Redirection vers les commandes après un délai
    setTimeout(() => {
      navigate("/orders");
    }, 2000);
  };

  const handlePaymentCancel = () => {
    setShowPaymentModal(false);
    setOrderId(null);
    setMsg("Paiement annulé. Votre commande reste en attente.");
  };

  if (!cart && !err) return <p style={{ padding: 40 }}>Chargement…</p>;

  return (
    <div style={{ padding: 40 }}>
      <h2>Mon panier</h2>
      {err && <p style={{ color: "tomato", fontWeight: 600 }}>{err}</p>}
      {msg && <p style={{ color: "green", fontWeight: 600 }}>{msg}</p>}
      
      {/* Message d'information pour les utilisateurs non connectés */}
      {!isAuthenticated() && items.length > 0 && (
        <div style={{ 
          backgroundColor: "#f0f9ff", 
          border: "1px solid #0ea5e9", 
          borderRadius: 8, 
          padding: 16, 
          marginBottom: 20 
        }}>
          <p style={{ margin: 0, color: "#0c4a6e", fontWeight: 600 }}>
            ℹ️ Vous n'êtes pas connecté
          </p>
          <p style={{ margin: "8px 0 0 0", color: "#0c4a6e", fontSize: 14 }}>
            Vous pouvez modifier votre panier, mais vous devrez vous connecter ou créer un compte pour passer commande.
          </p>
        </div>
      )}

      {items.length === 0 ? (
        <p>Panier vide.</p>
      ) : (
        <>
          <ul style={{ listStyle: "none", padding: 0, margin: 0, maxWidth: 680 }}>
            {items.map((it) => {
              const name = nameById.get(it.product_id) || it.product_id;
              const unit = priceById.get(it.product_id) || 0;
              const line = unit * it.quantity;
              return (
                <li
                  key={it.product_id}
                  style={{
                    display: "grid",
                    gridTemplateColumns: "1fr auto auto",
                    alignItems: "center",
                    gap: 12,
                    padding: "10px 0",
                    borderBottom: "1px solid #eee",
                  }}
                >
                  <div>
                    <div style={{ fontWeight: 700 }}>{name}</div>
                    <div style={{ color: "#64748b", fontSize: 14 }}>
                      {fmt.format(unit / 100)} / unité
                    </div>
                  </div>

                  <div style={{ display: "inline-flex", alignItems: "center", gap: 8 }}>
                    <button
                      onClick={() => dec(it.product_id)}
                      disabled={pending || it.quantity <= 1}
                      title="Retirer 1"
                      style={btn}
                    >
                      −
                    </button>
                    <span style={{ minWidth: 28, textAlign: "center", fontWeight: 700 }}>
                      {it.quantity}
                    </span>
                    <button
                      onClick={() => inc(it.product_id)}
                      disabled={pending}
                      title="Ajouter 1"
                      style={btn}
                    >
                      +
                    </button>
                    <button
                      onClick={() => removeAll(it.product_id)}
                      disabled={pending}
                      title="Supprimer l’article"
                      style={btnDanger}
                    >
                      Retirer
                    </button>
                  </div>

                  <div style={{ fontWeight: 700 }}>{fmt.format(line / 100)}</div>
                </li>
              );
            })}
          </ul>

          <div style={{ display: "flex", gap: 12, alignItems: "center", marginTop: 12 }}>
            <p style={{ margin: 0 }}>
              Total : <strong>{fmt.format(totalCents / 100)}</strong>
            </p>
            <button onClick={clearCart} disabled={pending} style={btnLight}>
              Vider le panier
            </button>
          </div>

          <div style={{ marginTop: 12 }}>
            {isAuthenticated() ? (
              <button
                onClick={checkout}
                disabled={pending}
                style={{ ...btnPrimary }}
              >
                {pending ? "Création de la commande..." : "Passer au paiement"}
              </button>
            ) : (
              <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
                <button
                  onClick={checkout}
                  disabled={pending}
                  style={{ 
                    ...btnPrimary, 
                    backgroundColor: "#dc2626",
                    opacity: 0.8
                  }}
                  title="Vous devez être connecté pour passer commande"
                >
                  🔒 Connexion requise pour le paiement
                </button>
                <div style={{ display: "flex", gap: 8 }}>
                  <a 
                    href="/login" 
                    style={{ 
                      ...btnPrimary, 
                      backgroundColor: "#059669",
                      textDecoration: "none",
                      display: "inline-block"
                    }}
                  >
                    Se connecter
                  </a>
                  <a 
                    href="/register" 
                    style={{ 
                      ...btnPrimary, 
                      backgroundColor: "#7c3aed",
                      textDecoration: "none",
                      display: "inline-block"
                    }}
                  >
                    Créer un compte
                  </a>
                </div>
              </div>
            )}
          </div>
        </>
      )}

      {/* Modal de paiement */}
      {orderId && (
        <PaymentModal
          orderId={orderId}
          amountCents={totalCents}
          onSuccess={handlePaymentSuccess}
          onCancel={handlePaymentCancel}
          isOpen={showPaymentModal}
        />
      )}
    </div>
  );
}

const btn = {
  background: "#fff",
  border: "1px solid #e5e7eb",
  borderRadius: 8,
  padding: "6px 10px",
  cursor: "pointer",
};

const btnLight = {
  background: "#fff",
  border: "1px solid #e5e7eb",
  borderRadius: 8,
  padding: "6px 10px",
  cursor: "pointer",
};

const btnPrimary = {
  background: "#2563eb",
  color: "#fff",
  border: "none",
  borderRadius: 8,
  padding: "10px 14px",
  cursor: "pointer",
  fontWeight: 700,
};

const btnDanger = {
  background: "#ef4444",
  color: "#fff",
  border: "none",
  borderRadius: 8,
  padding: "6px 10px",
  cursor: "pointer",
};