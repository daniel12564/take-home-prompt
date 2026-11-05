import { useAttention } from '../../api/dashboard';
import type { AttentionData, Finding, FindingSeverity } from '../../lib/types';
import { METRIC_LABELS, formatNumber } from './activity-summary';

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

const INSUFFICIENT_MESSAGES: Record<NonNullable<AttentionData['insufficient_reason']>, string> = {
  short_history:
    'Not enough history yet: more weeks of activity are needed to tell what needs attention this week.',
  no_events:
    'No activity has been recorded for this account yet, so there is nothing to compare against.',
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
  return `${value > 0 ? '+' : value < 0 ? '-' : ''}${formatNumber(Math.abs(value))}%`;
}

function FindingCard({ finding }: { finding: Finding }) {
  const severity = SEVERITY_STYLES[finding.severity];
  return (
    <li
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
      {error && (
        <p role='alert' className='text-sm text-red-700'>
          {error.message}
        </p>
      )}
      {data && data.insufficient_reason && (
        <p className='text-sm text-slate-500'>{INSUFFICIENT_MESSAGES[data.insufficient_reason]}</p>
      )}
      {data && !data.insufficient_reason && data.findings.length === 0 && (
        <p className='text-sm text-slate-500'>Nothing needs attention this week.</p>
      )}
      {data && data.findings.length > 0 && (
        <ul className='flex flex-col gap-3'>
          {data.findings.map((finding) => (
            <FindingCard
              key={`${finding.location}-${finding.kind}-${finding.event_types.join()}`}
              finding={finding}
            />
          ))}
        </ul>
      )}
    </section>
  );
}
