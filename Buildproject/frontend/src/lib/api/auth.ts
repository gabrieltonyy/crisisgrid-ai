import apiClient, { handleApiError } from './client';

export type UserRole = 'CITIZEN' | 'AUTHORITY' | 'ADMIN' | 'SYSTEM';

export interface RegisterData {
  name: string;
  email: string;
  password: string;
  phone_number?: string;
  role?: UserRole;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface User {
  id: string;
  name?: string | null;
  email?: string | null;
  phone_number?: string | null;
  role: UserRole;
  trust_score: number;
  is_active: boolean;
  email_verified: boolean;
  created_at: string;
  updated_at?: string | null;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export const authApi = {
  register: async (data: RegisterData): Promise<User> => {
    try {
      const response = await apiClient.post<User>('/auth/register', data);
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  login: async (data: LoginData): Promise<AuthResponse> => {
    try {
      const response = await apiClient.post<AuthResponse>('/auth/login', data);
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  getCurrentUser: async (): Promise<User> => {
    try {
      const response = await apiClient.get<User>('/auth/me');
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  logout: async (): Promise<void> => {
    try {
      await apiClient.post('/auth/logout');
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  refreshToken: async (): Promise<AuthResponse> => {
    try {
      const response = await apiClient.post<AuthResponse>('/auth/refresh');
      return response.data;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },
};

// Made with Bob
