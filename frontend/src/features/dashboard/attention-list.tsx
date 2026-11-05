import { useAttention } from '../../api/dashboard';
import { METRIC_LABELS, formatNumber, formatSigned, noEventsMessage } from '../../lib/format';
import type { AttentionData, EventType, Finding, FindingSeverity } from '../../lib/types';
import { dayLabel } from '../../lib/weeks';
import { ErrorMessage } from './error-message';

const SEVERITY_STYLES: Record<FindingSeverity, { label: string; card: string; badge: string }> = {
  critical: {
    label: 'Critical',
    card: 'border-red-300 bg-red-50',
    badge: 'bg-red-100 text-red-800',
  },
  warning: {
    label: 'Warning',
    card: 'border-amber-300 bg-amber-50',
    badge: 'bg-amber-100 text-amber-800',
  },
};

// A surge is worth a look but is not a problem, so it never takes the red styling of a drop,
// whatever its Severity; the Severity itself (label, order, data attribute) is unchanged.
function severityStyle(finding: Finding) {
  const style = SEVERITY_STYLES[finding.severity];
  if (finding.direction !== 'above') return style;
  return { ...SEVERITY_STYLES.warning, label: style.label };
}

const INSUFFICIENT_MESSAGES: Record<NonNullable<AttentionData['insufficient_reason']>, string> = {
  short_history:
    'Not enough history yet: more weeks of activity are needed to tell what needs attention this week.',
  no_events: noEventsMessage(),
};

function metricLabel(finding: Finding): string {
  if (finding.kind === 'no_activity') return 'All activity';
  return finding.event_types.map((eventType) => METRIC_LABELS[eventType]).join(', ');
}

function directionLabel(finding: Finding): string {
  if (finding.kind === 'no_activity') return 'No activity';
  return finding.direction === 'above' ? 'Above typical' : 'Dropped';
}

function formatPercent(value: number): string {
  return formatSigned(value, '%');
}

function AccountWideCard({ finding }: { finding: Finding }) {
  const severity = severityStyle(finding);
  const byMetric = Object.entries(finding.affected_by_metric ?? {}) as [EventType, number][];
  return (
    <li
      data-scope='account'
      data-severity={finding.severity}
      className='flex w-full flex-col gap-2 rounded-lg border-2 border-indigo-400 bg-indigo-50 p-5 shadow-sm'
    >
      <div className='flex flex-wrap items-center gap-2'>
        <span className='rounded bg-indigo-600 px-2 py-0.5 text-xs font-semibold uppercase tracking-wide text-white'>
          Account-wide
        </span>
        <span className='text-lg font-semibold text-slate-900'>
          {finding.affected_locations} of {finding.total_locations} locations
        </span>
        <span
          className={`ml-auto inline-block rounded-full px-2 py-0.5 text-xs font-medium ${severity.badge}`}
        >
          {severity.label}
        </span>
      </div>
      <div className='flex flex-wrap items-center gap-2'>
        <span className='text-sm text-slate-600'>{metricLabel(finding)}</span>
        <p className='text-sm font-medium text-slate-800'>{directionLabel(finding)}</p>
      </div>
      {byMetric.length > 0 && (
        <div className='flex flex-wrap gap-x-4 text-sm text-slate-600'>
          {byMetric.map(([eventType, count]) => (
            <p key={eventType}>
              {METRIC_LABELS[eventType]}: {count} of {finding.total_locations}
            </p>
          ))}
        </div>
      )}
      {finding.concentrated_on && (
        <p className='text-sm font-medium text-indigo-800'>
          Concentrated on {dayLabel(finding.concentrated_on)}
        </p>
      )}
      <p className='text-sm text-slate-700'>{finding.explanation}</p>
    </li>
  );
}

function FindingCard({ finding }: { finding: Finding }) {
  const severity = severityStyle(finding);
  return (
    <li
      data-scope='location'
      data-severity={finding.severity}
      className={`flex flex-col gap-2 rounded-lg border p-4 ${severity.card}`}
    >
      <div className='flex flex-wrap items-center gap-2'>
        <span className='font-semibold text-slate-900'>{finding.location}</span>
        <span className='text-sm text-slate-600'>{metricLabel(finding)}</span>
        <span
          className={`ml-auto inline-block rounded-full px-2 py-0.5 text-xs font-medium ${severity.badge}`}
        >
          {severity.label}
        </span>
      </div>
      <p className='text-sm font-medium text-slate-800'>{directionLabel(finding)}</p>
      {finding.kind === 'metric' && (
        <div className='flex flex-wrap gap-x-4 text-sm text-slate-600'>
          <p>This week: {finding.current}</p>
          {finding.baseline !== null && <p>Typical: {formatNumber(finding.baseline)}</p>}
          {finding.delta_pct !== null && <p>{formatPercent(finding.delta_pct)}</p>}
        </div>
      )}
      <p className='text-sm text-slate-700'>{finding.explanation}</p>
    </li>
  );
}

interface AttentionListProps {
  accountId: string | null;
  week: string;
}

export function AttentionList({ accountId, week }: AttentionListProps) {
  const { data, error, isPending } = useAttention(accountId, week);

  return (
    <section aria-labelledby='attention-list-title' className='flex flex-col gap-3'>
      <h2 id='attention-list-title' className='text-lg font-semibold text-slate-900'>
        Attention list
      </h2>
      {accountId === null && (
        <p className='text-sm text-slate-500'>Choose an account to see what needs attention.</p>
      )}
      {accountId !== null && isPending && !error && (
        <p role='status' className='text-sm text-slate-500'>
          Loading findings…
        </p>
      )}
      {error && <ErrorMessage error={error} />}
      {data && data.insufficient_reason && (
        <p className='text-sm text-slate-500'>{INSUFFICIENT_MESSAGES[data.insufficient_reason]}</p>
      )}
      {data && !data.insufficient_reason && data.findings.length === 0 && (
        <p className='text-sm text-slate-500'>Nothing needs attention this week.</p>
      )}
      {data && data.findings.length > 0 && (
        <ul className='flex flex-col gap-3'>
          {data.findings.map((finding) => {
            const key = `${finding.scope}-${finding.location}-${finding.kind}-${finding.direction}-${finding.event_types.join()}`;
            return finding.scope === 'account' ? (
              <AccountWideCard key={key} finding={finding} />
            ) : (
              <FindingCard key={key} finding={finding} />
            );
          })}
        </ul>
      )}
    </section>
  );
}
