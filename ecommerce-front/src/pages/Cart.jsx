// src/pages/Cart.jsx
import React, { useEffect, useMemo, useState } from "react";
import { api } from "../lib/api";

export default function Cart() {
  const [cart, setCart] = useState(null);
  const [products, setProducts] = useState([]);
  const [orderId, setOrderId] = useState(null);
  const [err, setErr] = useState("");
  const [msg, setMsg] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const [c, ps] = await Promise.all([api.getCart(), api.listProducts()]);
        setCart(c); setProducts(ps);
      } catch (e) { setErr(e.message); }
    })();
  }, []);

  const priceById = useMemo(() => {
    const m = new Map();
    products.forEach(p => m.set(p.id, p.price_cents));
    return m;
  }, [products]);

  const totalCents = useMemo(() => {
    if (!cart) return 0;
    return Object.values(cart.items || {}).reduce((sum, it) => {
      const unit = priceById.get(it.product_id) || 0;
      return sum + unit * it.quantity;
    }, 0);
  }, [cart, priceById]);

  const fmt = new Intl.NumberFormat("fr-FR", { style: "currency", currency: "EUR" });

  async function checkout() {
    setErr(""); setMsg("");
    try {
      const res = await api.checkout();
      setOrderId(res.order_id);
      setMsg("Commande créée. Renseigne ta carte pour payer ⬇️");
    } catch (e) { setErr(e.message); }
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
      await api.payByCard(orderId, payload);
      setMsg("✅ Paiement OK !");
    } catch (e) { setErr(e.message); }
  }

  if (!cart) return <p style={{ padding: 40 }}>Chargement…</p>;

  const items = Object.values(cart.items || {});

  return (
    <div style={{ padding: 40 }}>
      <h2>Mon panier</h2>
      {err && <p style={{ color: "tomato" }}>{err}</p>}
      {msg && <p style={{ color: "green" }}>{msg}</p>}

      {items.length === 0 ? (
        <p>Panier vide.</p>
      ) : (
        <>
          <ul>
            {items.map((it) => (
              <li key={it.product_id} style={{ marginBottom: 8 }}>
                {it.product_id} — Qté: {it.quantity}
              </li>
            ))}
          </ul>
          <p style={{ marginTop: 8 }}>Total: <strong>{fmt.format(totalCents / 100)}</strong></p>

          {!orderId ? (
            <button onClick={checkout} style={{ marginTop: 12, padding: "6px 12px" }}>
              Passer au paiement
            </button>
          ) : (
            <form onSubmit={pay} style={{ marginTop: 16, maxWidth: 360 }}>
              <h3>Paiement par carte</h3>
              <input name="card_number" placeholder="4242424242424242" required
                     style={{ display: "block", width: "100%", padding: 8, marginBottom: 8 }} />
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 8 }}>
                <input name="exp_month" type="number" placeholder="MM" required style={{ padding: 8 }} />
                <input name="exp_year" type="number" placeholder="YYYY" required style={{ padding: 8 }} />
                <input name="cvc" placeholder="123" required style={{ padding: 8 }} />
              </div>
              <button type="submit" style={{ marginTop: 10, padding: "6px 12px" }}>
                Payer
              </button>
            </form>
          )}
        </>
      )}
    </div>
  );
}