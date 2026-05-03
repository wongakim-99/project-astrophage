import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import api from '../lib/axios';
import type { StarResponse } from '../types/api';

export function useGalaxyStars(galaxyId: string | undefined) {
  return useQuery<StarResponse[]>({
    queryKey: ['stars', galaxyId],
    queryFn: () => api.get(`/galaxies/${galaxyId}/stars`).then((r) => r.data),
    enabled: !!galaxyId,
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
