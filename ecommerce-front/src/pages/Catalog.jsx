// src/pages/Catalog.jsx
//
// Page d'accueil avec liste des produits et ajout au panier (local ou serveur).
import React, { useEffect, useState } from "react";
import { api } from "../lib/api";
import { useAuth } from "../hooks/useAuth";
import "../styles/catalog.css";

export default function Catalog() {
  const { isAuthenticated } = useAuth();
  const [products, setProducts] = useState([]);
  const [msg, setMsg] = useState("");
  const [err, setErr] = useState("");

  useEffect(() => {
    (async () => {
      try {
        setErr(""); // Réinitialiser les erreurs
        const data = await api.listProducts();
        setProducts(data);
      } catch (e) {
        console.error('Erreur chargement produits:', e);
        setErr(`Erreur de chargement: ${e.message}`);
      }
    })();
  }, []);

  async function add(p) {
    setMsg("");
    setErr("");
    try {
      if (isAuthenticated()) {
        // Utilisateur connecté : ajouter au panier serveur
        await api.addToCart({ product_id: p.id, qty: 1 });
        setMsg(`✅ ${p.name} ajouté au panier`);
      } else {
        // Utilisateur non connecté : ajouter au panier local
        const localCartData = localStorage.getItem('localCart');
        const localCart = localCartData ? JSON.parse(localCartData) : { items: {} };
        
        const existingItem = localCart.items[p.id];
        if (existingItem) {
          localCart.items[p.id].quantity += 1;
        } else {
          localCart.items[p.id] = { product_id: p.id, quantity: 1 };
        }
        
        localStorage.setItem('localCart', JSON.stringify(localCart));
        setMsg(`✅ ${p.name} ajouté au panier (local)`);
      }
    } catch (e) {
      if (e.message.startsWith("HTTP 401"))
        setErr("Erreur de connexion. Vérifiez votre authentification.");
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
                  {(() => {
                    // Adapter aux différents formats d'API
                    const price = p.price_cents || (p.price ? Math.round(p.price * 100) : 0);
                    return price > 0 ? fmt.format(price / 100) : "Prix non disponible";
                  })()}
                </span>
                <span className="pcard__stock">
                  Stock&nbsp;:{" "}
                  {(() => {
                    // Adapter aux différents formats d'API
                    const stock = p.stock_qty || p.stock || 0;
                    return stock <= 0
                      ? "Rupture"
                      : stock < 5
                      ? "Faible"
                      : stock;
                  })()}
                </span>
              </div>
            </div>

            <div className="pcard__foot">
              <button
                onClick={() => add(p)}
                disabled={!p.active || (p.stock_qty || p.stock || 0) <= 0}
                className="btn btn--primary"
              >
                {(p.stock_qty || p.stock || 0) > 0 ? "Ajouter au panier" : "Rupture"}
              </button>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}