import { createContext } from 'react';
// Contexte minimal pour injection via Provider dédié.

/**
 * Contexte d'authentification (valeur fournie par `AuthProvider`).
 */
export const AuthContext = createContext();
