import { useContext } from 'react';
import { AuthContext } from '../contexts/AuthProvider';
import { AUTH_ERRORS } from '../constants/auth';

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error(AUTH_ERRORS.MUST_BE_WITHIN_PROVIDER);
  }
  return context;
}
