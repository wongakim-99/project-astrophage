import axios from 'axios';
import { create } from 'zustand';
import type { TokenResponse, UserResponse } from '../types/api';

interface AuthState {
  accessToken: string | null;
  isAuthenticated: boolean;
  isInitialized: boolean;
  user: UserResponse | null;
  setAccessToken: (token: string) => void;
  logout: () => void;
  login: (email: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  setUniversePublic: (isPublic: boolean) => Promise<void>;
  init: () => Promise<void>;
}

// auth 엔드포인트는 토큰 인터셉터 없이 raw axios 사용 (순환 의존성 방지)
const authAxios = axios.create({ baseURL: '/api', withCredentials: true });

async function fetchMe(token: string): Promise<UserResponse> {
  const { data } = await authAxios.get<UserResponse>('/auth/me', {
    headers: { Authorization: `Bearer ${token}` },
  });
  return data;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  accessToken: null,
  isAuthenticated: false,
  isInitialized: false,
  user: null,

  setAccessToken: (token) => set({ accessToken: token, isAuthenticated: true, isInitialized: true }),

  logout: async () => {
    try { await authAxios.post('/auth/logout'); } catch { /* ignore */ }
    set({ accessToken: null, isAuthenticated: false, isInitialized: true, user: null });
  },

  login: async (email, password) => {
    const { data } = await authAxios.post<TokenResponse>('/auth/login', { email, password });
    const user = await fetchMe(data.access_token);
    set({ accessToken: data.access_token, isAuthenticated: true, isInitialized: true, user });
  },

  register: async (username, email, password) => {
    const { data } = await authAxios.post<TokenResponse>('/auth/register', {
      username,
      email,
      password,
    });
    const user = await fetchMe(data.access_token);
    set({ accessToken: data.access_token, isAuthenticated: true, isInitialized: true, user });
  },

  setUniversePublic: async (isPublic) => {
    const token = get().accessToken;
    if (!token) return;
    const { data } = await authAxios.patch<UserResponse>(
      '/auth/me/settings',
      { is_universe_public: isPublic },
      { headers: { Authorization: `Bearer ${token}` } },
    );
    set({ user: data });
  },

  init: async () => {
    try {
      const { data } = await authAxios.post<TokenResponse>('/auth/refresh');
      const user = await fetchMe(data.access_token);
      set({ accessToken: data.access_token, isAuthenticated: true, isInitialized: true, user });
    } catch {
      set({ accessToken: null, isAuthenticated: false, isInitialized: true, user: null });
    }
  },
}));
