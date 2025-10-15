// src/pages/Cart.jsx
import React, { useEffect, useMemo, useState } from "react";
import { api } from "../lib/api";

export default function Cart() {
  const [cart, setCart] = useState(null);
  const [products, setProducts] = useState([]);
  const [orderId, setOrderId] = useState(null);
  const [err, setErr] = useState("");
  const [msg, setMsg] = useState("");
  const [pending, setPending] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const [c, ps] = await Promise.all([api.getCart(), api.listProducts()]);
        setCart(c);
        setProducts(ps);
      } catch (e) {
        setErr(e.message);
      }
    })();
  }, []);

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
      const c = await api.getCart();
      setCart(c);
    } catch (e) {
      setErr(e.message);
    }
  }

  // --- Actions ligne ---
  async function inc(product_id) {
    setErr(""); setMsg(""); setPending(true);
    try {
      await api.addToCart({ product_id, qty: 1 });
      await reload();
    } catch (e) {
      setErr(e.message);
    } finally {
      setPending(false);
    }
  }

  async function dec(product_id) {
    setErr(""); setMsg(""); setPending(true);
    try {
      await api.removeFromCart({ product_id, qty: 1 });
      await reload();
    } catch (e) {
      setErr(e.message);
    } finally {
      setPending(false);
    }
  }

  async function removeAll(product_id) {
    setErr(""); setMsg(""); setPending(true);
    try {
      // qty: 0 = supprimer l’article entièrement (supporté par ton API)
      await api.removeFromCart({ product_id, qty: 0 });
      await reload();
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
      // supprime chaque article (qty=0) en parallèle
      await Promise.all(items.map(it => api.removeFromCart({ product_id: it.product_id, qty: 0 })));
      await reload();
    } catch (e) {
      setErr(e.message);
    } finally {
      setPending(false);
    }
  }

  async function checkout() {
    setErr(""); setMsg("");
    try {
      const res = await api.checkout();
      setOrderId(res.order_id);
      setMsg("Commande créée. Renseigne ta carte pour payer ⬇️");
    } catch (e) {
      setErr(e.message);
    }
  }

  async function pay(e) {
    e.preventDefault();
    setErr(""); setMsg("");
    const form = new FormData(e.currentTarget);
    const payload = {
      card_number: form.get("card_number"),
      exp_month: Number(form.get("exp_month")),
      exp_year: Number(form.get("exp_year")),
      cvc: form.get("cvc"),
    };
    try {
      await api.payByCard(orderId, payload); // alias vers payOrder dans ton api.js
      setMsg("✅ Paiement OK !");
    } catch (e) {
      setErr(e.message);
    }
  }

  if (!cart) return <p style={{ padding: 40 }}>Chargement…</p>;

  return (
    <div style={{ padding: 40 }}>
      <h2>Mon panier</h2>
      {err && <p style={{ color: "tomato", fontWeight: 600 }}>{err}</p>}
      {msg && <p style={{ color: "green", fontWeight: 600 }}>{msg}</p>}

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

          {!orderId ? (
            <button
              onClick={checkout}
              disabled={pending}
              style={{ ...btnPrimary, marginTop: 12 }}
            >
              Passer au paiement
            </button>
          ) : (
            <form onSubmit={pay} style={{ marginTop: 16, maxWidth: 360 }}>
              <h3>Paiement par carte</h3>
              <input
                name="card_number"
                placeholder="4242424242424242"
                required
                style={{ display: "block", width: "100%", padding: 8, marginBottom: 8 }}
              />
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 8 }}>
                <input name="exp_month" type="number" placeholder="MM" required style={{ padding: 8 }} />
                <input name="exp_year" type="number" placeholder="YYYY" required style={{ padding: 8 }} />
                <input name="cvc" placeholder="123" required style={{ padding: 8 }} />
              </div>
              <button type="submit" disabled={pending} style={{ ...btnPrimary, marginTop: 10 }}>
                Payer
              </button>
            </form>
          )}
        </>
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