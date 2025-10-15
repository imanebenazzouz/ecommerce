// src/pages/Catalog.jsx
import React, { useEffect, useState } from "react";
import { api } from "../lib/api";
import "../styles/catalog.css";

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
    setMsg("");
    setErr("");
    try {
      await api.addToCart({ product_id: p.id, qty: 1 });
      setMsg(`✅ ${p.name} ajouté au panier`);
    } catch (e) {
      if (e.message.startsWith("HTTP 401"))
        setErr("Connecte-toi d’abord (menu Connexion).");
      else setErr(e.message);
    }
  }

  const fmt = new Intl.NumberFormat("fr-FR", {
    style: "currency",
    currency: "EUR",
  });

  return (
    <div className="cat">
      {/* Bandeau d’accueil */}
      <section className="hero">
        <h1 className="hero__title">Bienvenue sur notre boutique</h1>
        <p className="hero__subtitle">
          Découvrez nos meilleurs produits au meilleur prix 💎
        </p>
      </section>

      <div className="cat__header">
        <h2 className="cat__title">Catalogue</h2>
        <p className="cat__subtitle">{products.length} produit(s)</p>
      </div>

      {msg && <p className="cat__alert cat__alert--ok">{msg}</p>}
      {err && <p className="cat__alert cat__alert--ko">{err}</p>}

      <div className="cat__grid">
        {products.map((p) => (
          <article key={p.id} className="pcard">
            {/* Image produit (temporairement emoji) */}
            <div className="pcard__media">🛍️</div>

            <div className="pcard__body">
              <h3 className="pcard__title">{p.name}</h3>

              <div className="pcard__meta">
                <span className="pcard__price">
                  {fmt.format(p.price_cents / 100)}
                </span>
                <span className="pcard__stock">
                  Stock&nbsp;:{" "}
                  {p.stock_qty <= 0
                    ? "Rupture"
                    : p.stock_qty < 5
                    ? "Faible"
                    : p.stock_qty}
                </span>
              </div>
            </div>

            <div className="pcard__foot">
              <button
                onClick={() => add(p)}
                disabled={!p.active || p.stock_qty <= 0}
                className="btn btn--primary"
              >
                {p.stock_qty > 0 ? "Ajouter au panier" : "Rupture"}
              </button>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}