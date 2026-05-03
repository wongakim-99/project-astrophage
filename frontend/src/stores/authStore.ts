import axios from 'axios';
import { create } from 'zustand';
import type { TokenResponse, UserResponse } from '../types/api';

interface AuthState {
  accessToken: string | null;
  isAuthenticated: boolean;
  user: UserResponse | null;
  setAccessToken: (token: string) => void;
  logout: () => void;
  login: (email: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  init: () => Promise<void>;
}

// auth 엔드포인트는 토큰 인터셉터 없이 raw axios 사용 (순환 의존성 방지)
const authAxios = axios.create({ baseURL: '/api', withCredentials: true });

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null,
  isAuthenticated: false,
  user: null,

  setAccessToken: (token) => set({ accessToken: token, isAuthenticated: true }),

  logout: async () => {
    try { await authAxios.post('/auth/logout'); } catch { /* ignore */ }
    set({ accessToken: null, isAuthenticated: false, user: null });
  },

  login: async (email, password) => {
    const { data } = await authAxios.post<TokenResponse>('/auth/login', { email, password });
    set({ accessToken: data.access_token, isAuthenticated: true });
  },

  register: async (username, email, password) => {
    const { data } = await authAxios.post<TokenResponse>('/auth/register', {
      username,
      email,
      password,
    });
    set({ accessToken: data.access_token, isAuthenticated: true });
  },

  init: async () => {
    try {
      const { data } = await authAxios.post<TokenResponse>('/auth/refresh');
      set({ accessToken: data.access_token, isAuthenticated: true });
    } catch {
      set({ accessToken: null, isAuthenticated: false, user: null });
    }
  },
}));
