// src/pages/Register.jsx
import React, { useState } from "react";
import { api } from "../lib/api";

export default function Register() {
  const [form, setForm] = useState({ email:"", password:"", confirm:"", first_name:"", last_name:"", address:"" });
  const [err, setErr] = useState(""); const [ok, setOk] = useState("");

  const isEmail = (x) => /\S+@\S+\.\S+/.test(x);
  const isStrong = (x) => x.length >= 8 && /[A-Z]/.test(x) && /[a-z]/.test(x) && /\d/.test(x);

  async function submit(e){
    e.preventDefault(); setErr(""); setOk("");
    if (!isEmail(form.email)) return setErr("Email invalide");
    if (!isStrong(form.password)) return setErr("Mot de passe faible (8+, maj, min, chiffre)");
    if (form.password !== form.confirm) return setErr("Les mots de passe ne correspondent pas");
    if (!form.first_name || !form.last_name || !form.address) return setErr("Tous les champs sont obligatoires");
    try {
      await api.register({
        email: form.email, password: form.password,
        first_name: form.first_name, last_name: form.last_name, address: form.address,
      });
      setOk("Compte créé ✅ — connecte-toi"); setForm({ email:"", password:"", confirm:"", first_name:"", last_name:"", address:"" });
    } catch(e){ 
      let errorMessage = "Erreur lors de l'inscription, veuillez réessayer.";
      
      if (e?.message) {
        errorMessage = e.message;
      } else if (typeof e === 'string') {
        errorMessage = e;
      } else if (e?.toString) {
        errorMessage = e.toString();
      }
      
      setErr(errorMessage); 
    }
  }

  function onChange(e){ setForm({ ...form, [e.target.name]: e.target.value }); }

  return (
    <div style={{ padding: 40 }}>
      <h2>Inscription</h2>
      {ok && <p style={{ color: "green" }}>{ok}</p>}
      {err && <p style={{ color: "tomato" }}>{err}</p>}
      <form onSubmit={submit} style={{ maxWidth: 420 }}>
        <label> Email
          <input name="email" type="email" value={form.email} onChange={onChange} required style={{ display:"block", width:"100%", padding:8, margin:"6px 0 10px" }} />
        </label>
        <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap: 10 }}>
          <label> Prénom
            <input name="first_name" value={form.first_name} onChange={onChange} required style={{ width:"100%", padding:8, marginTop:6 }} />
          </label>
          <label> Nom
            <input name="last_name" value={form.last_name} onChange={onChange} required style={{ width:"100%", padding:8, marginTop:6 }} />
          </label>
        </div>
        <label> Adresse
          <input name="address" value={form.address} onChange={onChange} required style={{ display:"block", width:"100%", padding:8, margin:"6px 0 10px" }} />
        </label>
        <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap: 10 }}>
          <label> Mot de passe
            <input name="password" type="password" value={form.password} onChange={onChange} required style={{ width:"100%", padding:8, marginTop:6 }} />
          </label>
          <label> Confirmer
            <input name="confirm" type="password" value={form.confirm} onChange={onChange} required style={{ width:"100%", padding:8, marginTop:6 }} />
          </label>
        </div>
        <button type="submit" style={{ marginTop: 12, padding: "8px 14px" }}>Créer mon compte</button>
      </form>
    </div>
  );
}