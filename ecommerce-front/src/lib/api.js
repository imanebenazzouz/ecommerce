const API = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

// Fonction pour obtenir le token depuis localStorage
function getToken() {
  return localStorage.getItem("token");
}

async function request(path, init = {}) {
  const token = getToken();
  const headers = { "Content-Type": "application/json", ...(init.headers || {}) };
  
  // Ajouter le token d'authentification si disponible
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(API + path, {
    credentials: "include",
    headers,
    ...init,
  });
  
  let body = null;
  try { 
    body = await res.json(); 
  } catch { 
    // pas de JSON dans la réponse
  }

  if (!res.ok) {
    // on normalise un message lisible
    const msg = body?.message || body?.detail || `Erreur HTTP ${res.status}`;
    const err = new Error(msg);
    err.status = res.status;
    throw err;
  }
  return body;
}

export const api = {
  // Authentification
  register: ({ email, password, first_name, last_name, address }) =>
    request("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, first_name, last_name, address }),
    }),

  login: ({ email, password }) =>
    request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  logout: () =>
    request("/auth/logout", {
      method: "POST",
    }),

  // Produits
  listProducts: () =>
    request("/products"),

  // Panier
  getCart: () =>
    request("/cart"),

  addToCart: ({ product_id, qty }) =>
    request("/cart/add", {
      method: "POST",
      body: JSON.stringify({ product_id, qty }),
    }),

  removeFromCart: ({ product_id, qty }) =>
    request("/cart/remove", {
      method: "POST",
      body: JSON.stringify({ product_id, qty }),
    }),

  // Commandes
  checkout: () =>
    request("/orders/checkout", {
      method: "POST",
    }),

  payByCard: (orderId, { card_number, exp_month, exp_year, cvc }) =>
    request(`/orders/${orderId}/pay`, {
      method: "POST",
      body: JSON.stringify({ card_number, exp_month, exp_year, cvc }),
    }),

  getOrders: () =>
    request("/orders"),
};
