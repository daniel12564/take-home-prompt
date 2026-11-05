import { useQuery } from '@tanstack/react-query';

import type { ActivitySummaryData, AttentionData } from '../lib/types';
import { apiGet } from './client';

export const dashboardKeys = {
  summary: (accountId: string, week: string, location: string | null) =>
    ['summary', accountId, week, location] as const,
  attention: (accountId: string, week: string) => ['attention', accountId, week] as const,
};

export function useActivitySummary(
  accountId: string | null,
  week: string,
  location: string | null,
) {
  return useQuery({
    queryKey: dashboardKeys.summary(accountId ?? '', week, location),
    queryFn: () => {
      const params = new URLSearchParams({ week_start: week });
      if (location) params.set('location', location);
      return apiGet<ActivitySummaryData>(
        `/accounts/${accountId}/dashboard/activity-summary/?${params}`,
      );
    },
    enabled: accountId !== null,
  });
}

export function useAttention(accountId: string | null, week: string) {
  return useQuery({
    queryKey: dashboardKeys.attention(accountId ?? '', week),
    queryFn: () => {
      const params = new URLSearchParams({ week_start: week });
      return apiGet<AttentionData>(`/accounts/${accountId}/dashboard/attention/?${params}`);
    },
    enabled: accountId !== null,
  });
}
