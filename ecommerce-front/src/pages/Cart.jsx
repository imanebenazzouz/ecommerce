// src/pages/Cart.jsx
//
// Panier avec fallback local: incrément, décrément, vidage, checkout + paiement.
import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import { useAuth } from "../hooks/useAuth";
import PaymentModal from "../components/PaymentModal";

export default function Cart() {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [cart, setCart] = useState(null);
  const [products, setProducts] = useState([]);
  const [orderId, setOrderId] = useState(null);
  const [err, setErr] = useState("");
  const [msg, setMsg] = useState("");
  const [pending, setPending] = useState(false);
  const [showPaymentModal, setShowPaymentModal] = useState(false);

  useEffect(() => {
    // Attendre que l'authentification soit complètement chargée
    if (authLoading) {
      return;
    }

    (async () => {
      try {
        setErr(""); // Réinitialiser les erreurs
        setPending(true);
        
        // Charger les produits d'abord
        console.log('🛒 Chargement des produits...');
        const ps = await api.listProducts();
        setProducts(ps);
        console.log('✅ Produits chargés');

        if (isAuthenticated()) {
          // Utilisateur connecté : récupérer le panier du serveur
          console.log('🛒 Chargement du panier serveur...');
          try {
            const c = await api.getCart();
            setCart(c);
            console.log('✅ Panier serveur chargé');
          } catch (cartError) {
            console.warn('Erreur chargement panier serveur:', cartError);
            if (cartError.status === 401) {
              // Session expirée, basculer sur le panier local
              const localCart = getLocalCart();
              setCart(localCart);
              setErr("Session expirée, utilisation du panier local");
            } else {
              // Autre erreur, essayer le panier local en fallback
              const localCart = getLocalCart();
              setCart(localCart);
              setErr(`Erreur serveur: ${cartError.message}. Utilisation du panier local.`);
            }
          }
        } else {
          // Utilisateur non connecté : récupérer le panier local
          console.log('🛒 Chargement du panier local...');
          const localCart = getLocalCart();
          setCart(localCart);
          console.log('✅ Panier local chargé');
        }
      } catch (e) {
        console.error('Erreur chargement général:', e);
        // En cas d'erreur générale, essayer au moins le panier local
        const localCart = getLocalCart();
        setCart(localCart);
        setErr(`Erreur de chargement: ${e.message}. Utilisation du panier local.`);
      } finally {
        setPending(false);
      }
    })();
  }, [isAuthenticated, authLoading]);

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
    products.forEach((p) => {
      // Adapter aux différents formats d'API
      const price = p.price_cents || (p.price ? Math.round(p.price * 100) : 0);
      m.set(p.id, price);
    });
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
        try {
          const c = await api.getCart();
          setCart(c);
          setErr(""); // Effacer les erreurs en cas de succès
        } catch (cartError) {
          console.warn('Erreur reload panier serveur:', cartError);
          if (cartError.status === 401) {
            // Session expirée, basculer sur le panier local
            const localCart = getLocalCart();
            setCart(localCart);
            setErr("Session expirée, utilisation du panier local");
          } else {
            // Autre erreur, garder le panier local
            const localCart = getLocalCart();
            setCart(localCart);
            setErr(`Erreur serveur: ${cartError.message}. Utilisation du panier local.`);
          }
        }
      } else {
        const localCart = getLocalCart();
        setCart(localCart);
        setErr(""); // Effacer les erreurs en cas de succès
      }
    } catch (e) {
      console.error('Erreur reload général:', e);
      setErr(`Erreur de rechargement: ${e.message}`);
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
    // Protection contre les doubles clics - mettre pending IMMÉDIATEMENT
    if (pending) return; // Si déjà en cours, ignorer le clic
    
    setErr(""); setMsg("");
    setPending(true); // Mettre pending AVANT toute autre opération
    
    try {
      // Vérification d'authentification avant le paiement
      if (!isAuthenticated()) {
        setPending(false);
        // Redirection vers login avec paramètre de retour
        navigate("/login?next=/cart");
        return;
      }

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

  const handlePaymentSuccess = () => {
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

  // Afficher le chargement pendant l'initialisation de l'authentification
  if (authLoading) {
    return (
      <div style={{ padding: 40, textAlign: 'center' }}>
        <div style={{ 
          display: 'inline-block',
          width: '40px',
          height: '40px',
          border: '4px solid #f3f3f3',
          borderTop: '4px solid #2563eb',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite',
          marginBottom: '16px'
        }}></div>
        <p>Initialisation de votre session...</p>
      </div>
    );
  }

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

      {/* Message d'information pour les erreurs de serveur */}
      {isAuthenticated() && err && err.includes("Erreur serveur") && (
        <div style={{ 
          backgroundColor: "#fef3c7", 
          border: "1px solid #f59e0b", 
          borderRadius: 8, 
          padding: 16, 
          marginBottom: 20 
        }}>
          <p style={{ margin: 0, color: "#92400e", fontWeight: 600 }}>
            ⚠️ Problème de connexion au serveur
          </p>
          <p style={{ margin: "8px 0 0 0", color: "#92400e", fontSize: 14 }}>
            Votre panier local est affiché. Les modifications seront synchronisées dès que la connexion sera rétablie.
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
                      {unit > 0 ? fmt.format(unit / 100) : "Prix non disponible"} / unité
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

                  <div style={{ fontWeight: 700 }}>
                    {line > 0 ? fmt.format(line / 100) : "Prix non disponible"}
                  </div>
                </li>
              );
            })}
          </ul>

          <div style={{ display: "flex", gap: 12, alignItems: "center", marginTop: 12 }}>
            <p style={{ margin: 0 }}>
              Total : <strong>{totalCents > 0 ? fmt.format(totalCents / 100) : "0,00 €"}</strong>
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

// Animation pour le spinner
const spinKeyframes = `
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
`;

// Injecter les styles si pas déjà présents
if (!document.getElementById('cart-spinner-styles')) {
  const style = document.createElement('style');
  style.id = 'cart-spinner-styles';
  style.textContent = spinKeyframes;
  document.head.appendChild(style);
}