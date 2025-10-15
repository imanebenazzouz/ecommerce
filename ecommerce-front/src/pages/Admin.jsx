// src/pages/Admin.jsx
import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";

export default function Admin() {
  const navigate = useNavigate();

  // Sécurité front rapide (on cache la page si pas admin)
  const role = (typeof localStorage !== "undefined" && localStorage.getItem("role")) || "user";
  useEffect(() => {
    if (role !== "admin") navigate("/", { replace: true });
  }, [role, navigate]);

  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");
  const [msg, setMsg] = useState("");

  // Formulaire de création
  const [form, setForm] = useState({
    name: "",
    description: "",
    price_eur: "", // on saisit en euros côté UI, on convertit en cents pour l’API
    stock_qty: "",
    active: true,
  });

  const fmt = useMemo(() => new Intl.NumberFormat("fr-FR", { style: "currency", currency: "EUR" }), []);

  function eurToCents(v) {
    if (v === "" || v === null || v === undefined) return 0;
    const n = Number(String(v).replace(",", "."));
    return Number.isFinite(n) ? Math.round(n * 100) : 0;
  }

  function centsToEur(c) {
    if (c === null || c === undefined) return "";
    return (c / 100).toFixed(2);
  }

  async function load() {
    setLoading(true);
    setErr("");
    try {
      const data = await api.adminListProducts();
      setItems(data);
    } catch (e) {
      setErr(e.message || "Impossible de charger les produits.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function handleCreate(e) {
    e.preventDefault();
    setErr(""); setMsg("");
    try {
      const body = {
        name: form.name.trim(),
        description: form.description.trim(),
        price_cents: eurToCents(form.price_eur),
        stock_qty: Number(form.stock_qty || 0),
        active: !!form.active,
      };
      if (!body.name) throw new Error("Nom obligatoire");
      const created = await api.adminCreateProduct(body);
      setMsg(`✅ Produit créé : ${created.name}`);
      setForm({ name: "", description: "", price_eur: "", stock_qty: "", active: true });
      await load();
    } catch (e) {
      setErr(e.message || "Erreur lors de la création.");
    }
  }

  async function handleUpdate(id, patch) {
    setErr(""); setMsg("");
    try {
      // On convertit si besoin
      const b = { ...patch };
      if (Object.prototype.hasOwnProperty.call(b, "price_eur")) {
        b.price_cents = eurToCents(b.price_eur);
        delete b.price_eur;
      }
      if (Object.prototype.hasOwnProperty.call(b, "stock_qty")) {
        b.stock_qty = Number(b.stock_qty);
      }
      const updated = await api.adminUpdateProduct(id, b);
      setMsg(`✅ Modifié : ${updated.name}`);
      await load();
    } catch (e) {
      setErr(e.message || "Erreur de mise à jour.");
    }
  }

  async function handleDelete(id) {
    if (!confirm("Supprimer ce produit ?")) return;
    setErr(""); setMsg("");
    try {
      await api.adminDeleteProduct(id);
      setMsg("🗑️ Produit supprimé");
      await load();
    } catch (e) {
      setErr(e.message || "Erreur de suppression.");
    }
  }

  return (
    <div style={{ padding: 24 }}>
      <header style={{ marginBottom: 16 }}>
        <h2 style={{ margin: 0 }}>🛠️ Espace administrateur</h2>
        <p style={{ color: "#64748b", marginTop: 6 }}>
          Gérer le catalogue produits (créer, éditer, supprimer).
        </p>
      </header>

      {/* Alerts */}
      {msg && (
        <div style={{
          padding: "10px 12px", borderRadius: 8, marginBottom: 12,
          background: "#ecfdf5", color: "#065f46", border: "1px solid #a7f3d0", fontWeight: 600
        }}>
          {msg}
        </div>
      )}
      {err && (
        <div style={{
          padding: "10px 12px", borderRadius: 8, marginBottom: 12,
          background: "#fef2f2", color: "#991b1b", border: "1px solid #fecaca", fontWeight: 600
        }}>
          {err}
        </div>
      )}

      {/* Formulaire Création */}
      <section style={{
        border: "1px solid #e5e7eb", borderRadius: 12, padding: 16, marginBottom: 20,
        background: "#fff", boxShadow: "0 1px 2px rgba(0,0,0,.04)"
      }}>
        <h3 style={{ marginTop: 0, marginBottom: 10 }}>Créer un produit</h3>
        <form onSubmit={handleCreate} style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
          <label style={{ display: "block" }}>
            <div style={{ fontWeight: 600, marginBottom: 4 }}>Nom</div>
            <input
              value={form.name}
              onChange={(e) => setForm(f => ({ ...f, name: e.target.value }))}
              required
              style={fieldStyle}
              placeholder="Ex: T-Shirt Logo"
            />
          </label>

          <label style={{ display: "block" }}>
            <div style={{ fontWeight: 600, marginBottom: 4 }}>Prix (EUR)</div>
            <input
              value={form.price_eur}
              onChange={(e) => setForm(f => ({ ...f, price_eur: e.target.value }))}
              required
              inputMode="decimal"
              style={fieldStyle}
              placeholder="19.99"
            />
          </label>

          <label style={{ display: "block" }}>
            <div style={{ fontWeight: 600, marginBottom: 4 }}>Stock</div>
            <input
              value={form.stock_qty}
              onChange={(e) => setForm(f => ({ ...f, stock_qty: e.target.value }))}
              required
              inputMode="numeric"
              style={fieldStyle}
              placeholder="100"
            />
          </label>

          <label style={{ display: "block" }}>
            <div style={{ fontWeight: 600, marginBottom: 4 }}>Actif</div>
            <select
              value={form.active ? "1" : "0"}
              onChange={(e) => setForm(f => ({ ...f, active: e.target.value === "1" }))}
              style={fieldStyle}
            >
              <option value="1">Oui</option>
              <option value="0">Non</option>
            </select>
          </label>

          <label style={{ display: "block", gridColumn: "1 / -1" }}>
            <div style={{ fontWeight: 600, marginBottom: 4 }}>Description</div>
            <textarea
              value={form.description}
              onChange={(e) => setForm(f => ({ ...f, description: e.target.value }))}
              rows={3}
              style={{ ...fieldStyle, resize: "vertical" }}
              placeholder="Coton bio, coupe droite…"
            />
          </label>

          <div style={{ gridColumn: "1 / -1", display: "flex", gap: 8, justifyContent: "flex-end" }}>
            <button type="submit" style={primaryBtn}>Créer</button>
            <button type="button" style={secondaryBtn} onClick={() => setForm({ name:"", description:"", price_eur:"", stock_qty:"", active:true })}>
              Réinitialiser
            </button>
          </div>
        </form>
      </section>

      {/* Liste produits */}
      <section>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 10 }}>
          <h3 style={{ margin: 0 }}>Produits ({items.length})</h3>
          <button onClick={load} style={secondaryBtn}>Rafraîchir</button>
        </div>

        {loading ? (
          <p style={{ color: "#64748b" }}>Chargement…</p>
        ) : items.length === 0 ? (
          <div style={{
            padding: 24, textAlign: "center", border: "1px solid #e5e7eb",
            borderRadius: 12, background: "#fff"
          }}>
            Aucun produit.
          </div>
        ) : (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 14 }}>
            {items.map(p => (
              <article key={p.id} style={{
                border: "1px solid #e5e7eb", borderRadius: 12, background: "#fff",
                boxShadow: "0 1px 2px rgba(0,0,0,.04)", overflow: "hidden"
              }}>
                <div style={{
                  padding: 12, borderBottom: "1px solid #eef2f7", background: "#f8fafc",
                  display: "flex", alignItems: "center", justifyContent: "space-between"
                }}>
                  <strong>{p.name}</strong>
                  <span style={{ fontWeight: 700, color: "#2563eb" }}>{fmt.format(p.price_cents / 100)}</span>
                </div>

                <div style={{ padding: 12, display: "grid", gap: 8 }}>
                  <div style={{ color: "#64748b", fontSize: 14 }}>{p.description || "—"}</div>

                  <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
                    <small>Stock:</small>
                    <input
                      defaultValue={p.stock_qty}
                      type="number"
                      min="0"
                      onBlur={(e) => {
                        const val = Number(e.target.value);
                        if (val !== p.stock_qty && Number.isFinite(val)) handleUpdate(p.id, { stock_qty: val });
                      }}
                      style={{ ...fieldStyle, width: 110, padding: "6px 8px" }}
                    />

                    <small>Actif:</small>
                    <select
                      defaultValue={p.active ? "1" : "0"}
                      onChange={(e) => handleUpdate(p.id, { active: e.target.value === "1" })}
                      style={{ ...fieldStyle, width: 100, padding: "6px 8px" }}
                    >
                      <option value="1">Oui</option>
                      <option value="0">Non</option>
                    </select>
                  </div>

                  <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
                    <small>Nom:</small>
                    <input
                      defaultValue={p.name}
                      onBlur={(e) => {
                        const v = e.target.value.trim();
                        if (v && v !== p.name) handleUpdate(p.id, { name: v });
                      }}
                      style={{ ...fieldStyle, flex: 1, padding: "6px 8px" }}
                    />
                  </div>

                  <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
                    <small>Prix (EUR):</small>
                    <input
                      defaultValue={centsToEur(p.price_cents)}
                      inputMode="decimal"
                      onBlur={(e) => {
                        const v = e.target.value;
                        if (v !== centsToEur(p.price_cents)) handleUpdate(p.id, { price_eur: v });
                      }}
                      style={{ ...fieldStyle, width: 140, padding: "6px 8px" }}
                    />
                  </div>

                  <div style={{ display: "flex", gap: 8, justifyContent: "flex-end", marginTop: 6 }}>
                    <button onClick={() => handleDelete(p.id)} style={dangerBtn}>Supprimer</button>
                  </div>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

const fieldStyle = {
  width: "100%",
  padding: "10px 12px",
  borderRadius: 10,
  border: "1px solid #e5e7eb",
  background: "#fff",
  outline: "none",
};

const primaryBtn = {
  background: "#2563eb",
  color: "#fff",
  border: "none",
  borderRadius: 10,
  padding: "10px 14px",
  fontWeight: 700,
  cursor: "pointer",
};

const secondaryBtn = {
  background: "#fff",
  color: "#0f172a",
  border: "1px solid #e5e7eb",
  borderRadius: 10,
  padding: "8px 12px",
  fontWeight: 700,
  cursor: "pointer",
};

const dangerBtn = {
  background: "#ef4444",
  color: "#fff",
  border: "none",
  borderRadius: 10,
  padding: "8px 12px",
  fontWeight: 700,
  cursor: "pointer",
};