import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import type { ReactNode } from 'react';
import { getAuth, logout } from '../../lib/allauth';
import { getUser } from '~/lib/django';
import type { FalucheStatus } from '~/lib/falucheStatus';

interface User {
  email: string;
  has_usable_password: boolean;
  [key: string]: any;
  user: {
    id: number;
  };
  profile: {
    address: string;
    birth_date: string;
    can_host_peoples: boolean;
    car_seats: number;
    city: string;
    country: string;
    date_joined: string;
    email: string;
    faluche_nickname: string;
    faluche_status?: FalucheStatus | null;
    first_name: string;
    has_car: boolean;
    home_available_beds: number;
    home_rules: string;
    id: number;
    is_active: boolean;
    is_staff: boolean;
    is_superuser: boolean;
    last_login: string;
    last_name: string;
    phone_number: string;
    zip_code: string;
  };
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (userData: User) => void;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth doit être utilisé à l\'intérieur d\'un AuthProvider');
  }
  return context;
}

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  // Référence pour suivre si un refreshUser est en cours
  const isRefreshing = useRef(false);

  const refreshUser = async () => {
    // Éviter les appels en parallèle
    if (isRefreshing.current) return;

    try {
      isRefreshing.current = true;
      setIsLoading(true);
      setError(null);

      const response = await getAuth();
      const profileResponse = await getUser();
      const profile = await profileResponse.json();

      if (response.status === 200) {
        if (response.meta?.is_authenticated && response.data) {
          const userData = {
            ...response.data,
            profile: profile
          }
          setUser(userData);
        } else {
          setUser(null);
        }
      } else {
        setUser(null);
        if (response.message) {
          setError(response.message);
        }
      }
    } catch (err) {
      setUser(null);
      setError('Erreur lors de la récupération des informations utilisateur');
      console.error('Auth error:', err);
    } finally {
      setIsLoading(false);
      isRefreshing.current = false;
    }
  };

  const handleLogout = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await logout();

      if (response.status === 200) {
        setUser(null);
      } else {
        setError(response.message || 'Erreur lors de la déconnexion');
      }
    } catch (err) {
      setError('Erreur lors de la déconnexion');
      console.error('Logout error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const loginUser = (userData: User) => {
    setUser(userData);
  };

  // Écouteur d'événement pour les changements d'authentification
  useEffect(() => {
    // Vérifier si on est côté client
    if (typeof window === 'undefined' || typeof document === 'undefined') {
      return;
    }

    const handleAuthChange = (event: CustomEvent) => {
      // Ignorer les événements si refreshUser est déjà en cours
      if (isRefreshing.current) return;

      if (event.detail?.meta?.is_authenticated) {
        refreshUser();
      } else {
        setUser(null);
      }
    };

    document.addEventListener('allauth.auth.change', handleAuthChange as EventListener);

    // Vérifier l'état d'authentification au chargement
    refreshUser();

    return () => {
      document.removeEventListener('allauth.auth.change', handleAuthChange as EventListener);
    };
  }, []);

  const value = {
    user,
    isAuthenticated: !!user,
    isLoading,
    error,
    login: loginUser,
    logout: handleLogout,
    refreshUser
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
