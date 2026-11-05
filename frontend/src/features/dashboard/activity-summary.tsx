import { useActivitySummary } from '../../api/dashboard';
import type { ActivitySummaryData, EventType, Metric } from '../../lib/types';
import { ErrorMessage } from './error-message';
import { StatusBadge } from './status-badge';

export const METRIC_LABELS: Record<EventType, string> = {
  call_received: 'Calls received',
  lead_created: 'Leads created',
  appointment_set: 'Appointments set',
};

export function formatNumber(value: number): string {
  return Number.isInteger(value) ? String(value) : value.toFixed(1);
}

function formatSigned(value: number, suffix = ''): string {
  if (value === 0) return `0${suffix}`;
  return `${value > 0 ? '+' : '-'}${formatNumber(Math.abs(value))}${suffix}`;
}

function formatDelta(metric: Metric): string | null {
  if (metric.delta === null) return null;
  if (metric.delta_pct === null) return formatSigned(metric.delta);
  return `${formatSigned(metric.delta)} (${formatSigned(metric.delta_pct, '%')})`;
}

function insufficientMessage(reason: ActivitySummaryData['insufficient_reason'], location: string | null) {
  if (reason === 'no_events') {
    return `No activity has been recorded for this ${location ? 'location' : 'account'} yet, so there is nothing to compare against.`;
  }
  return 'Not enough history yet: more weeks of activity are needed to judge this week.';
}

function weeksOfHistory(weeks: number): string {
  return `${weeks} ${weeks === 1 ? 'week' : 'weeks'}`;
}

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
      {error && <ErrorMessage error={error} />}
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
              {metric.status === 'insufficient_data' ? (
                <p className='text-sm text-slate-500'>
                  {insufficientMessage(data.insufficient_reason, data.location)}
                </p>
              ) : (
                <div className='text-sm text-slate-600'>
                  {metric.baseline !== null && <p>Typical: {formatNumber(metric.baseline)}</p>}
                  {formatDelta(metric) && <p>{formatDelta(metric)}</p>}
                </div>
              )}
            </article>
          ))}
        </div>
      )}
      {data && data.metrics.some((metric) => metric.status !== 'insufficient_data') && (
        <p className='text-xs text-slate-500'>
          Typical values are based on the {weeksOfHistory(data.baseline_weeks_used)} before this
          one.
        </p>
      )}
    </section>
  );
}
