import { useMutation, useQueries, useQuery, useQueryClient } from '@tanstack/react-query';
import api from '../lib/axios';
import { useAuthStore } from '../stores/authStore';
import type { GalaxyResponse, StarPublicResponse, StarResponse } from '../types/api';

export function useGalaxyStars(galaxyId: string | undefined) {
  return useQuery<StarResponse[]>({
    queryKey: ['stars', galaxyId],
    queryFn: () => api.get(`/stars/galaxy/${galaxyId}`).then((r) => r.data),
    enabled: !!galaxyId,
  });
}

export function useAllGalaxyStars(galaxies: GalaxyResponse[]) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const queries = useQueries({
    queries: galaxies.map((galaxy) => ({
      queryKey: ['stars', galaxy.id],
      queryFn: () => api.get<StarResponse[]>(`/stars/galaxy/${galaxy.id}`).then((r) => r.data),
      enabled: isAuthenticated,
    })),
  });

  return {
    stars: queries.flatMap((query, index) =>
      (query.data ?? []).map((star) => ({
        ...star,
        galaxy: galaxies[index],
      })),
    ),
    isLoading: queries.some((query) => query.isLoading),
    isError: queries.some((query) => query.isError),
  };
}

export function usePublicStars() {
  return useQuery<StarPublicResponse[]>({
    queryKey: ['public-stars'],
    queryFn: () => api.get('/explore').then((r) => r.data),
  });
}

export function usePublicStar(username: string | undefined, slug: string | undefined) {
  return useQuery<StarPublicResponse>({
    queryKey: ['public-star', username, slug],
    queryFn: () => api.get(`/${username}/stars/${slug}`).then((r) => r.data),
    enabled: !!username && !!slug,
  });
}

interface CreateStarParams {
  title: string;
  slug: string;
  content: string;
  galaxy_id: string;
}

export function useCreateStar() {
  const queryClient = useQueryClient();
  return useMutation<StarResponse, Error, CreateStarParams>({
    mutationFn: (body) => api.post('/stars', body).then((r) => r.data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['stars', data.galaxy_id] });
    },
  });
}
