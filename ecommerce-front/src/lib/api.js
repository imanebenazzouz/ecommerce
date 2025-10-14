const API = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

async function request(path, init = {}) {
  const res = await fetch(API + path, {
    credentials: "include",                    // si le backend met un cookie de session
    headers: { "Content-Type": "application/json", ...(init.headers || {}) },
    ...init,
  });
  let body = null;
  try { body = await res.json(); } catch { /* pas de JSON */ }

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
  // ...déjà présent
  register: ({ email, password, first_name, last_name, address }) =>
    request("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, first_name, last_name, address }),
    }),
  // login, logout, me ... (déjà faits)
};
