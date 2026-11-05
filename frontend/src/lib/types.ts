export interface ApiSuccess<T> {
  success: true;
  data: T;
}

export interface ApiFailure {
  success: false;
  message: string;
  errors: Record<string, string[]>;
  error_code: string;
}

export type ApiEnvelope<T> = ApiSuccess<T> | ApiFailure;

export interface Account {
  id: number;
  name: string;
  timezone: string;
  location_count: number;
}

export type EventType = 'call_received' | 'lead_created' | 'appointment_set';

export type MetricStatus = 'typical' | 'above' | 'below' | 'insufficient_data';

export interface Metric {
  event_type: EventType;
  current: number;
  baseline: number | null;
  delta: number | null;
  delta_pct: number | null;
  status: MetricStatus;
}

export interface ActivitySummaryData {
  account_id: number;
  week_start: string;
  week_end: string;
  location: string | null;
  baseline_weeks_used: number;
  metrics: Metric[];
}
