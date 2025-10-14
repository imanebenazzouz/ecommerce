import React from "react";
import { Routes, Route, Link } from "react-router-dom";
import Catalog from "./pages/Catalog";
import Login from "./pages/Login";
import Register from "./pages/Register"; // +++

export default function App() {
  return (
    <div style={{ padding: 40, fontFamily: "Arial, sans-serif" }}>
      <nav style={{ marginBottom: 24 }}>
        <Link to="/" style={{ marginRight: 16 }}>Accueil</Link>
        <Link to="/login" style={{ marginRight: 16 }}>Connexion</Link>
        <Link to="/register">Inscription</Link> {/* +++ */}
      </nav>

      <h1>Mon e-commerce 🛍️</h1>

      <Routes>
        <Route path="/" element={<Catalog />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} /> {/* +++ */}
      </Routes>
    </div>
  );
}