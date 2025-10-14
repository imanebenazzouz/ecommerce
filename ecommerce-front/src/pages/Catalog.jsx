// src/pages/Catalog.jsx
import React, { useEffect, useState } from "react";
import { api } from "../lib/api";

export default function Catalog() {
  const [products, setProducts] = useState([]);
  const [msg, setMsg] = useState("");
  const [err, setErr] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const data = await api.listProducts();
        setProducts(data);
      } catch (e) {
        setErr(e.message);
      }
    })();
  }, []);

  async function add(p) {
    setMsg(""); setErr("");
    try {
      await api.addToCart({ product_id: p.id, qty: 1 });
      setMsg(`✅ ${p.name} ajouté au panier`);
    } catch (e) {
      if (e.message.startsWith("HTTP 401")) setErr("Connecte-toi d’abord (menu Connexion).");
      else setErr(e.message);
    }
  }

  const fmt = new Intl.NumberFormat("fr-FR", { style: "currency", currency: "EUR" });

  return (
    <div style={{ paddingTop: 20 }}>
      <h2>Catalogue</h2>
      {msg && <p style={{ color: "green" }}>{msg}</p>}
      {err && <p style={{ color: "tomato" }}>{err}</p>}
      <ul>
        {products.map((p) => (
          <li key={p.id} style={{ marginBottom: 10 }}>
            <strong>{p.name}</strong> — {fmt.format(p.price_cents / 100)} — Stock: {p.stock_qty}
            <button
              onClick={() => add(p)}
              disabled={!p.active || p.stock_qty <= 0}
              style={{ marginLeft: 10, padding: "4px 10px" }}
            >
              {p.stock_qty > 0 ? "Ajouter" : "Rupture"}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}