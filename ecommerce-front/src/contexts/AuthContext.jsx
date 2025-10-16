import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../lib/api';

const AuthContext = createContext();

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

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
    } catch (error) {
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
