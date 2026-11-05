import { useQuery } from '@tanstack/react-query';

import type { HealthStatus } from '../lib/types';
import { apiGet } from './client';

export function useHealth() {
  return useQuery({
    queryKey: ['health'],
    queryFn: () => apiGet<HealthStatus>('/health/'),
  });
}
