import { useQuery } from '@tanstack/react-query';

import type { Account } from '../lib/types';
import { apiGet } from './client';

export const accountKeys = {
  all: ['accounts'] as const,
  locations: (accountId: string) => ['locations', accountId] as const,
};

export function useAccounts() {
  return useQuery({
    queryKey: accountKeys.all,
    queryFn: () => apiGet<Account[]>('/accounts/'),
  });
}

export function useLocations(accountId: string | null) {
  return useQuery({
    queryKey: accountKeys.locations(accountId ?? ''),
    queryFn: () => apiGet<string[]>(`/accounts/${accountId}/locations/`),
    enabled: accountId !== null,
  });
}
