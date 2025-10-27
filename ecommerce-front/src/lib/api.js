// src/lib/api.js
const API = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

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
    let msg;
    if (payload) {
      if (typeof payload === "string") {
        msg = payload;
      } else if (payload.detail) {
        msg = payload.detail;
      } else if (payload.message) {
        msg = payload.message;
      } else if (payload.error) {
        msg = payload.error;
      } else {
        msg = `Erreur ${res.status}: ${JSON.stringify(payload)}`;
      }
    } else {
      msg = `Erreur HTTP ${res.status}`;
    }
    
    const err = new Error(msg);
    err.status = res.status;
    err.payload = payload;
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
  const response = await request("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  
  // Le backend retourne { token }
  const token = response.token;
  setToken(token);

  // récupère l'utilisateur courant (contient is_admin)
  let user = null;
  try { 
    user = await me(); 
  } catch (error) {
    console.warn('Erreur lors de la récupération des données utilisateur:', error);
    // Si on ne peut pas récupérer l'utilisateur, on déconnecte
    setToken(null);
    throw new Error('Erreur d\'authentification');
  }
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

async function getProduct(productId) {
  return request(`/products/${productId}`);
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

async function clearCart() {
  return request("/cart/clear", { method: "POST" });
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

// GET /orders/:id
async function getOrder(orderId) {
  return request(`/orders/${orderId}`);
}

// POST /orders/:id/cancel
async function cancelOrder(orderId) {
  return request(`/orders/${orderId}/cancel`, { method: "POST" });
}

// GET /orders/:id/invoice
async function getInvoice(orderId) {
  return request(`/orders/${orderId}/invoice`);
}

// GET /orders/:id/invoice/download - téléchargement PDF
async function downloadInvoicePDF(orderId) {
  const token = getToken();
  const response = await fetch(API + `/orders/${orderId}/invoice/download`, {
    method: 'GET',
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });

  if (!response.ok) {
    throw new Error(`Erreur de téléchargement: ${response.status}`);
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `facture_${orderId.slice(-8)}.pdf`;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}

// GET /orders/:id/tracking
async function getOrderTracking(orderId) {
  return request(`/orders/${orderId}/tracking`);
}

// POST /orders/{order_id}/pay (système de paiement)
async function processPayment({ orderId, cardNumber, expMonth, expYear, cvc, postalCode, phone, streetNumber, streetName }) {
  return request(`/orders/${orderId}/pay`, {
    method: "POST",
    body: JSON.stringify({ 
      card_number: cardNumber, 
      exp_month: expMonth, 
      exp_year: expYear, 
      cvc: cvc,
      postal_code: postalCode,
      phone: phone,
      street_number: streetNumber,
      street_name: streetName
    }),
  });
}

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

// GET /admin/orders/:id
async function adminGetOrder(orderId) {
  return request(`/admin/orders/${orderId}`);
}

// GET /admin/orders/:id/status
async function adminGetOrderStatus(orderId) {
  return request(`/admin/orders/${orderId}/status`);
}

// POST /admin/orders/:id/validate
async function adminValidateOrder(order_id) {
  return request(`/admin/orders/${order_id}/validate`, { method: "POST" });
}

// POST /admin/orders/:id/ship
async function adminShipOrder(order_id, delivery_data = {}) {
  // Données par défaut pour l'expédition
  const defaultDeliveryData = {
    transporteur: "Colissimo",
    tracking_number: null,
    delivery_status: "PREPAREE",
    ...delivery_data
  };
  
  return request(`/admin/orders/${order_id}/ship`, { 
    method: "POST", 
    body: JSON.stringify(defaultDeliveryData) 
  });
}

// POST /admin/orders/:id/mark-delivered
async function adminMarkDelivered(order_id) {
  return request(`/admin/orders/${order_id}/mark-delivered`, { method: "POST" });
}

// POST /admin/orders/:id/refund  { amount_cents? }
async function adminRefundOrder(order_id, body = {}) {
  return request(`/admin/orders/${order_id}/refund`, { method: "POST", body: JSON.stringify(body) });
}

/* =========================
   SUPPORT CLIENT
   ========================= */

// POST /support/threads { subject, order_id? }
async function createSupportThread({ subject, order_id = null }) {
  return request("/support/threads", {
    method: "POST",
    body: JSON.stringify({ subject, order_id }),
  });
}

// GET /support/threads
async function listSupportThreads() {
  return request("/support/threads");
}

// GET /support/threads/:id
async function getSupportThread(threadId) {
  return request(`/support/threads/${threadId}`);
}

// POST /support/threads/:id/messages { content }
async function postSupportMessage(threadId, { content }) {
  return request(`/support/threads/${threadId}/messages`, {
    method: "POST",
    body: JSON.stringify({ content }),
  });
}

// POST /support/threads/:id/mark-read
async function markSupportThreadAsRead(threadId) {
  return request(`/support/threads/${threadId}/mark-read`, { method: "POST" });
}

/* =========================
   ADMIN SUPPORT
   ========================= */

// GET /admin/support/threads
async function adminListSupportThreads() {
  try {
    return await request("/admin/support/threads");
  } catch (error) {
    // Erreur adminListSupportThreads
    throw new Error(`Erreur lors du chargement des fils de discussion: ${error.message || "Erreur inconnue"}`);
  }
}

// GET /admin/support/threads/:id
async function adminGetSupportThread(threadId) {
  try {
    if (!threadId) {
      throw new Error("ID du fil de discussion manquant");
    }
    return await request(`/admin/support/threads/${threadId}`);
  } catch (error) {
    // Erreur adminGetSupportThread
    throw new Error(`Erreur lors du chargement du fil: ${error.message || "Erreur inconnue"}`);
  }
}

// POST /admin/support/threads/:id/close
async function adminCloseSupportThread(threadId) {
  try {
    if (!threadId) {
      throw new Error("ID du fil de discussion manquant");
    }
    return await request(`/admin/support/threads/${threadId}/close`, { method: "POST" });
  } catch (error) {
    // Erreur adminCloseSupportThread
    throw new Error(`Erreur lors de la fermeture du fil: ${error.message || "Erreur inconnue"}`);
  }
}

// POST /admin/support/threads/:id/messages { content }
async function adminPostSupportMessage(threadId, { content }) {
  try {
    if (!threadId) {
      throw new Error("ID du fil de discussion manquant");
    }
    if (!content || !content.trim()) {
      throw new Error("Le contenu du message ne peut pas être vide");
    }
    return await request(`/admin/support/threads/${threadId}/messages`, {
      method: "POST",
      body: JSON.stringify({ content: content.trim() }),
    });
  } catch (error) {
    // Erreur adminPostSupportMessage
    throw new Error(`Erreur lors de l'envoi du message: ${error.message || "Erreur inconnue"}`);
  }
}

export const api = {
  // Auth
  register, login, logout, me, updateProfile, setToken,

  // Catalogue / Panier / Commandes (user)
  listProducts, getProduct,
  viewCart, getCart,
  addToCart, removeFromCart, clearCart,
  checkout,
  payOrder, payByCard, processPayment,
  myOrders, getOrders, getOrder, cancelOrder,
  getInvoice, downloadInvoicePDF,

  // Admin Produits
  adminListProducts,
  adminCreateProduct,
  adminUpdateProduct,
  adminDeleteProduct,

  // Admin Commandes
  adminListOrders,
  adminGetOrder,
  adminGetOrderStatus,
  adminValidateOrder,
  adminShipOrder,
  adminMarkDelivered,
  adminRefundOrder,
  
  // Suivi de livraison
  getOrderTracking,

  // Support Client
  createSupportThread,
  listSupportThreads,
  getSupportThread,
  postSupportMessage,
  markSupportThreadAsRead,

  // Admin Support
  adminListSupportThreads,
  adminGetSupportThread,
  adminCloseSupportThread,
  adminPostSupportMessage,
};