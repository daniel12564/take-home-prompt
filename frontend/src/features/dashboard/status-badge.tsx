import type { MetricStatus } from '../../lib/types';

const BADGES: Record<MetricStatus, { label: string; className: string }> = {
  typical: { label: 'Typical', className: 'bg-green-100 text-green-800' },
  below: { label: 'Below typical', className: 'bg-red-100 text-red-800' },
  above: { label: 'Above typical', className: 'bg-amber-100 text-amber-800' },
  insufficient_data: { label: 'Insufficient data', className: 'bg-slate-100 text-slate-600' },
};

interface StatusBadgeProps {
  status: MetricStatus;
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const { label, className } = BADGES[status];
  return (
    <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${className}`}>
      {label}
    </span>
  );
}
