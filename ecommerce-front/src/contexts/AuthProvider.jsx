import React, { useState, useEffect } from 'react';
// Contexte d'authentification complet avec persistance localStorage et API.
import { api } from '../lib/api';
import { AuthContext } from './AuthContext';

/**
 * Provider d'authentification global.
 * @param {{children: React.ReactNode}} props
 * @returns {JSX.Element}
 */
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  // Fonction de déconnexion locale (pour éviter les références circulaires)
  const clearAuth = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('role');
    localStorage.removeItem('localCart');
  };

  // Vérifier l'authentification au chargement
  useEffect(() => {
    const initAuth = async () => {
      try {
        const storedToken = localStorage.getItem('token');
        if (storedToken) {
          setToken(storedToken);
          // Vérifier si le token est encore valide
          const userData = await api.me();
          setUser(userData);
        }
      } catch {
        console.warn('Token invalide, déconnexion automatique');
        clearAuth();
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = async (userData, tokenData) => {
    try {
      setUser(userData);
      setToken(tokenData);
      localStorage.setItem('token', tokenData);
      localStorage.setItem('user', JSON.stringify(userData));
      return { success: true };
    } catch (error) {
      // Erreur lors de la connexion
      // En cas d'erreur, nettoyer l'état
      clearAuth();
      throw error;
    }
  };

  const logout = () => {
    clearAuth();
  };

  const updateUser = (userData) => {
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const isAuthenticated = () => {
    return !!user && !!token;
  };

  const isAdmin = () => {
    return user?.is_admin === true;
  };

  const value = {
    user,
    token,
    loading,
    login,
    logout,
    updateUser,
    isAuthenticated,
    isAdmin
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export { AuthContext };
