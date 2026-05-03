import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/authStore';
import { authApi, RegisterData } from '@/lib/api/auth';

export function useAuth(requireAuth: boolean = false) {
  const router = useRouter();
  const {
    user,
    token,
    isAuthenticated,
    isLoading,
    setAuth,
    clearAuth,
    setLoading,
    hasRole,
    hasAnyRole,
    isTokenExpired,
  } = useAuthStore();

  useEffect(() => {
    const initAuth = async () => {
      setLoading(true);
      const storedToken = localStorage.getItem('auth_token') || token;
      
      if (!storedToken || isTokenExpired()) {
        clearAuth();
        if (requireAuth) {
          router.replace('/login');
        }
        setLoading(false);
        return;
      }

      localStorage.setItem('auth_token', storedToken);

      if (storedToken && user) {
        setAuth(storedToken, user);
      } else if (storedToken) {
        try {
          const userData = await authApi.getCurrentUser();
          setAuth(storedToken, userData);
        } catch (error) {
          clearAuth();
          if (requireAuth) {
            router.replace('/login');
          }
        }
      }
      
      setLoading(false);
    };

    initAuth();
  }, [clearAuth, isTokenExpired, requireAuth, router, setAuth, setLoading, token, user]);

  const login = async (email: string, password: string) => {
    try {
      const response = await authApi.login({ email, password });
      setAuth(response.access_token, response.user);
      return { success: true, user: response.user };
    } catch (error) {
      return { 
        success: false, 
        error: error instanceof Error ? error.message : 'Login failed'
      };
    }
  };

  const register = async (data: RegisterData) => {
    try {
      const user = await authApi.register(data);
      return { success: true, user };
    } catch (error) {
      return { 
        success: false, 
        error: error instanceof Error ? error.message : 'Registration failed'
      };
    }
  };

  const refreshSession = async () => {
    const response = await authApi.refreshToken();
    setAuth(response.access_token, response.user);
    return response.user;
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } catch (error) {
      // Ignore errors on logout
    } finally {
      clearAuth();
      router.replace('/login');
    }
  };

  return {
    user,
    token,
    isAuthenticated,
    isLoading,
    login,
    register,
    refreshSession,
    logout,
    hasRole,
    hasAnyRole,
  };
}

// Made with Bob
