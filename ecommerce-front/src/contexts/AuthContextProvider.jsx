import React, { useState, useEffect } from 'react';
// Variante légère du provider d'authentification utilisée par certaines pages.
import { api } from '../lib/api';
import { AuthContext } from './AuthContext';

/**
 * Provider d'authentification minimal (token localStorage + api.me()).
 * @param {{children: React.ReactNode}} props
 * @returns {JSX.Element}
 */
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in on app start
    const token = localStorage.getItem("token");
    if (token) {
      // Récupérer les vraies données utilisateur
      api.me().then(userData => {
        setUser({ ...userData, token });
      }).catch(() => {
        // Token invalide, nettoyer
        localStorage.removeItem("token");
        setUser(null);
      }).finally(() => {
        setLoading(false);
      });
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (userData, token) => {
    localStorage.setItem("token", token);
    // Récupérer les données utilisateur complètes
    try {
      const fullUserData = await api.me();
      setUser({ ...fullUserData, token });
    } catch {
      // Fallback sur les données fournies
      setUser({ ...userData, token });
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    setUser(null);
  };

  const isAuthenticated = () => {
    return !!user && !!localStorage.getItem("token");
  };

  const value = {
    user,
    login,
    logout,
    isAuthenticated,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
