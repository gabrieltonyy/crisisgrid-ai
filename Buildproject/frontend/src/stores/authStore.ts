import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { jwtDecode } from 'jwt-decode';
import type { User, UserRole } from '@/lib/api/auth';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  
  setAuth: (token: string, user: User) => void;
  clearAuth: () => void;
  setUser: (user: User) => void;
  setLoading: (loading: boolean) => void;
  hasRole: (role: UserRole) => boolean;
  hasAnyRole: (roles: UserRole[]) => boolean;
  
  // Helper to check if token is expired
  isTokenExpired: () => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: true,

      setAuth: (token: string, user: User) => {
        localStorage.setItem('auth_token', token);
        set({ token, user, isAuthenticated: true, isLoading: false });
      },

      clearAuth: () => {
        localStorage.removeItem('auth_token');
        set({ token: null, user: null, isAuthenticated: false, isLoading: false });
      },

      setUser: (user: User) => {
        set({ user });
      },

      setLoading: (loading: boolean) => {
        set({ isLoading: loading });
      },

      hasRole: (role: UserRole) => {
        return get().user?.role === role;
      },

      hasAnyRole: (roles: UserRole[]) => {
        const role = get().user?.role;
        return Boolean(role && roles.includes(role));
      },

      isTokenExpired: () => {
        const token = get().token || (typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null);
        if (!token) return true;
        
        try {
          const decoded: { exp?: number } = jwtDecode(token);
          return !decoded.exp || decoded.exp * 1000 < Date.now();
        } catch {
          return true;
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ 
        token: state.token,
        user: state.user,
      }),
    }
  )
);

// Made with Bob
