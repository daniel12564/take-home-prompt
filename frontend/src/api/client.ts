import type { ApiEnvelope } from '../lib/types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';

export class ApiError extends Error {
  readonly errorCode: string;
  readonly errors: Record<string, string[]>;

  constructor(message: string, errorCode: string, errors: Record<string, string[]> = {}) {
    super(message);
    this.name = 'ApiError';
    this.errorCode = errorCode;
    this.errors = errors;
  }
}

export async function apiGet<T>(path: string): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      headers: { Accept: 'application/json' },
    });
  } catch {
    throw new ApiError('Could not reach the API.', 'NETWORK_ERROR');
  }

  let body: ApiEnvelope<T>;
  try {
    body = (await response.json()) as ApiEnvelope<T>;
  } catch {
    throw new ApiError('The API returned an unreadable response.', 'INVALID_RESPONSE');
  }

  if (!body.success) {
    throw new ApiError(body.message, body.error_code, body.errors);
  }
  return body.data;
}
