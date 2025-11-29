'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, Tokens } from '@/lib/api';
import { STORAGE_KEYS, ROUTES, UserRole } from '@/lib/constants';

interface AuthContextType {
  user: User | null;
  tokens: Tokens | null;
  isAuthenticated: boolean;
  login: (user: User, tokens: Tokens) => void;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [tokens, setTokens] = useState<Tokens | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Load user data from localStorage on mount
    if (typeof window !== 'undefined') {
      const storedUser = localStorage.getItem(STORAGE_KEYS.USER_DATA);
      const storedAccessToken = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
      const storedRefreshToken = localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);

      if (storedUser && storedAccessToken && storedRefreshToken) {
        try {
          setUser(JSON.parse(storedUser));
          setTokens({
            access: storedAccessToken,
            refresh: storedRefreshToken,
          });
        } catch (error) {
          console.error('Error parsing stored user data:', error);
          localStorage.removeItem(STORAGE_KEYS.USER_DATA);
          localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
          localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
        }
      }
      setIsLoading(false);
    }
  }, []);

  const login = (userData: User, userTokens: Tokens) => {
    setUser(userData);
    setTokens(userTokens);
    
    if (typeof window !== 'undefined') {
      localStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(userData));
      localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, userTokens.access);
      localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, userTokens.refresh);
    }
  };

  const logout = () => {
    setUser(null);
    setTokens(null);
    
    if (typeof window !== 'undefined') {
      localStorage.removeItem(STORAGE_KEYS.USER_DATA);
      localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
      localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
      window.location.href = ROUTES.LOGIN;
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        tokens,
        isAuthenticated: !!user && !!tokens,
        login,
        logout,
        isLoading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

