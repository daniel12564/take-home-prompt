import type { EventType } from './types';

export const METRIC_LABELS: Record<EventType, string> = {
  call_received: 'Calls received',
  lead_created: 'Leads created',
  appointment_set: 'Appointments set',
};

export function formatNumber(value: number): string {
  return Number.isInteger(value) ? String(value) : value.toFixed(1);
}

export function formatSigned(value: number, suffix = ''): string {
  if (value === 0) return `0${suffix}`;
  return `${value > 0 ? '+' : '-'}${formatNumber(Math.abs(value))}${suffix}`;
}

export function noEventsMessage(location: string | null = null): string {
  return `No activity has been recorded for this ${location ? 'location' : 'account'} yet, so there is nothing to compare against.`;
}
