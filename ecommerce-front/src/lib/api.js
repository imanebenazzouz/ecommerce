// src/lib/api.js
const API = import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8000";

// --- Token helpers ---
function getToken() {
  return localStorage.getItem("token");
}
export function setToken(t) {
  if (t) localStorage.setItem("token", t);
  else localStorage.removeItem("token");
}

// --- HTTP helper ---
async function request(path, init = {}) {
  const token = getToken();
  const headers = {
    "Content-Type": "application/json",
    ...(init.headers || {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };

  const res = await fetch(API + path, {
    credentials: "include", // ok même si tu n'utilises pas de cookies
    ...init,
    headers,
  });

  // Essaye de lire la réponse (JSON ou texte simple)
  let payload = null;
  const text = await res.text();
  if (text) {
    try { payload = JSON.parse(text); }
    catch { payload = text; }
  }

  if (!res.ok) {
    const msg = (payload && (payload.detail || payload.message)) || payload || `HTTP ${res.status}`;
    const err = new Error(typeof msg === "string" ? msg : `HTTP ${res.status}`);
    err.status = res.status;
    throw err;
  }
  return payload;
}

/* =========================
   AUTH
   ========================= */

// POST /auth/register
async function register({ email, password, first_name, last_name, address }) {
  return request("/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password, first_name, last_name, address }),
  });
}

// POST /auth/login → { token }  (+ /auth/me pour le rôle)
async function login({ email, password }) {
  const { token } = await request("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  setToken(token);

  // récupère l'utilisateur courant (contient is_admin)
  let user = null;
  try { user = await me(); } catch {}
  return { token, user };
}

// GET /auth/me → { id, email, first_name, last_name, address, is_admin }
async function me() {
  return request("/auth/me");
}

// PUT /auth/profile → met à jour { first_name?, last_name?, address? }
async function updateProfile({ first_name, last_name, address }) {
  const body = {};
  if (first_name !== undefined) body.first_name = first_name;
  if (last_name !== undefined) body.last_name = last_name;
  if (address !== undefined) body.address = address;
  return request("/auth/profile", { method: "PUT", body: JSON.stringify(body) });
}

// POST /auth/logout
async function logout() {
  try {
    await request("/auth/logout", { method: "POST" });
  } finally {
    setToken(null);
  }
}

/* =========================
   CATALOGUE (public)
   ========================= */

// GET /products
async function listProducts() {
  return request("/products");
}

/* =========================
   PANIER & COMMANDES (user)
   ========================= */

// GET /cart
async function viewCart() {
  return request("/cart");
}

// alias pour compat avec ton code existant
const getCart = viewCart;

// POST /cart/add  { product_id, qty }
async function addToCart({ product_id, qty = 1 }) {
  return request("/cart/add", { method: "POST", body: JSON.stringify({ product_id, qty }) });
}

// POST /cart/remove  { product_id, qty }
async function removeFromCart({ product_id, qty = 1 }) {
  return request("/cart/remove", { method: "POST", body: JSON.stringify({ product_id, qty }) });
}

// POST /orders/checkout  → { order_id, total_cents, status }
async function checkout() {
  return request("/orders/checkout", { method: "POST" });
}

// POST /orders/{order_id}/pay  { card_number, exp_month, exp_year, cvc }
async function payOrder(order_id, { card_number, exp_month, exp_year, cvc }) {
  return request(`/orders/${order_id}/pay`, {
    method: "POST",
    body: JSON.stringify({ card_number, exp_month, exp_year, cvc }),
  });
}

// alias pour compat (ton code utilisait payByCard)
const payByCard = payOrder;

// GET /orders
async function myOrders() {
  return request("/orders");
}

// alias compat
const getOrders = myOrders;

/* =========================
   ADMIN — Produits
   ========================= */

// GET /admin/products
async function adminListProducts() {
  return request("/admin/products");
}

// POST /admin/products  { name, description, price_cents, stock_qty, active }
async function adminCreateProduct(body) {
  return request("/admin/products", { method: "POST", body: JSON.stringify(body) });
}

// PUT /admin/products/:id
async function adminUpdateProduct(id, body) {
  return request(`/admin/products/${id}`, { method: "PUT", body: JSON.stringify(body) });
}

// DELETE /admin/products/:id
async function adminDeleteProduct(id) {
  return request(`/admin/products/${id}`, { method: "DELETE" });
}

/* =========================
   ADMIN — Commandes
   ========================= */

// GET /admin/orders?user_id=...
async function adminListOrders(params = {}) {
  const qs = new URLSearchParams(params).toString();
  return request(`/admin/orders${qs ? `?${qs}` : ""}`);
}

// POST /admin/orders/:id/validate
async function adminValidateOrder(order_id) {
  return request(`/admin/orders/${order_id}/validate`, { method: "POST" });
}

// POST /admin/orders/:id/ship
async function adminShipOrder(order_id) {
  return request(`/admin/orders/${order_id}/ship`, { method: "POST" });
}

// POST /admin/orders/:id/mark-delivered
async function adminMarkDelivered(order_id) {
  return request(`/admin/orders/${order_id}/mark-delivered`, { method: "POST" });
}

// POST /admin/orders/:id/refund  { amount_cents? }
async function adminRefundOrder(order_id, body = {}) {
  return request(`/admin/orders/${order_id}/refund`, { method: "POST", body: JSON.stringify(body) });
}

export const api = {
  // Auth
  register, login, logout, me, updateProfile, setToken,

  // Catalogue / Panier / Commandes (user)
  listProducts,
  viewCart, getCart,
  addToCart, removeFromCart,
  checkout,
  payOrder, payByCard,
  myOrders, getOrders,

  // Admin Produits
  adminListProducts,
  adminCreateProduct,
  adminUpdateProduct,
  adminDeleteProduct,

  // Admin Commandes
  adminListOrders,
  adminValidateOrder,
  adminShipOrder,
  adminMarkDelivered,
  adminRefundOrder,
};