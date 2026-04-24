import axios from 'axios';
import { useAuthStore } from '../stores/authStore';

const instance = axios.create({
  baseURL: '/api',
  withCredentials: true, // For HTTP-only refresh tokens
});

instance.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

instance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    // Handle 401 Unauthorized globally for token refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const res = await axios.post('/api/auth/refresh', {}, { withCredentials: true });
        const newToken = res.data.access_token;
        useAuthStore.getState().setAccessToken(newToken);
        instance.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
        return instance(originalRequest);
      } catch (e) {
        useAuthStore.getState().logout();
        window.location.href = '/auth/login';
        return Promise.reject(e);
      }
    }
    return Promise.reject(error);
  }
);

export default instance;
