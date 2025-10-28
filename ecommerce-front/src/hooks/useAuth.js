import { useContext } from 'react';
// Hook de confort pour consommer le contexte d'authentification.
import { AuthContext } from '../contexts/AuthContext';
import { AUTH_ERRORS } from '../constants/auth';

/**
 * Accède au contexte d'authentification.
 * @returns {{ user: any, login: Function, logout: Function, isAuthenticated: Function, loading: boolean } | any}
 */
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error(AUTH_ERRORS.MUST_BE_WITHIN_PROVIDER);
  }
  return context;
}
