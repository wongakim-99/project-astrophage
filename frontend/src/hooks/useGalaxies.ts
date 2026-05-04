import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import api from '../lib/axios';
import { useAuthStore } from '../stores/authStore';
import type { GalaxyResponse } from '../types/api';

export function useGalaxies() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  return useQuery<GalaxyResponse[]>({
    queryKey: ['galaxies'],
    queryFn: () => api.get('/galaxies').then((r) => r.data),
    enabled: isAuthenticated,
  });
}

interface CreateGalaxyParams {
  name: string;
  slug: string;
  color: string;
}

export function useCreateGalaxy() {
  const queryClient = useQueryClient();
  return useMutation<GalaxyResponse, Error, CreateGalaxyParams>({
    mutationFn: (body) => api.post('/galaxies', body).then((r) => r.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['galaxies'] });
    },
  });
}
