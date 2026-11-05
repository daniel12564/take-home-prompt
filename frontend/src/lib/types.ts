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
