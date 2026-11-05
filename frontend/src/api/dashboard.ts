import { useQuery } from '@tanstack/react-query';

import type { ActivitySummaryData } from '../lib/types';
import { apiGet } from './client';

export const dashboardKeys = {
  summary: (accountId: string, week: string, location: string | null) =>
    ['summary', accountId, week, location] as const,
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
