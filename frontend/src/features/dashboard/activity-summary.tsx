import { useActivitySummary } from '../../api/dashboard';
import type { EventType } from '../../lib/types';
import { StatusBadge } from './status-badge';

const METRIC_LABELS: Record<EventType, string> = {
  call_received: 'Calls received',
  lead_created: 'Leads created',
  appointment_set: 'Appointments set',
};

interface ActivitySummaryProps {
  accountId: string | null;
  week: string;
  location: string | null;
}

export function ActivitySummary({ accountId, week, location }: ActivitySummaryProps) {
  const { data, error, isPending } = useActivitySummary(accountId, week, location);

  return (
    <section aria-labelledby='activity-summary-title' className='flex flex-col gap-3'>
      <h2 id='activity-summary-title' className='text-lg font-semibold text-slate-900'>
        Activity summary
      </h2>
      {accountId === null && (
        <p className='text-sm text-slate-500'>Choose an account to see its activity.</p>
      )}
      {accountId !== null && isPending && !error && (
        <p role='status' className='text-sm text-slate-500'>
          Loading activity…
        </p>
      )}
      {error && (
        <p role='alert' className='text-sm text-red-700'>
          {error.message}
        </p>
      )}
      {data && data.metrics.length === 0 && (
        <p className='text-sm text-slate-500'>No activity data for this selection.</p>
      )}
      {data && data.metrics.length > 0 && (
        <div className='grid gap-4 sm:grid-cols-3'>
          {data.metrics.map((metric) => (
            <article
              key={metric.event_type}
              aria-label={METRIC_LABELS[metric.event_type]}
              className='flex flex-col gap-2 rounded-lg border border-slate-200 bg-white p-4'
            >
              <h3 className='text-sm font-medium text-slate-600'>
                {METRIC_LABELS[metric.event_type]}
              </h3>
              <p className='text-3xl font-semibold text-slate-900'>{metric.current}</p>
              <StatusBadge status={metric.status} />
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
