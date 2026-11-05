import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen, within } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { ActivitySummary } from './activity-summary';

const PAYLOAD = {
  account_id: 1,
  week_start: '2026-07-20',
  week_end: '2026-07-26',
  location: null,
  baseline_weeks_used: 0,
  metrics: [
    {
      event_type: 'call_received',
      current: 17,
      baseline: null,
      delta: null,
      delta_pct: null,
      status: 'insufficient_data',
    },
    {
      event_type: 'lead_created',
      current: 4,
      baseline: null,
      delta: null,
      delta_pct: null,
      status: 'insufficient_data',
    },
    {
      event_type: 'appointment_set',
      current: 0,
      baseline: null,
      delta: null,
      delta_pct: null,
      status: 'insufficient_data',
    },
  ],
};

function stubFetch(body: unknown) {
  const fetchMock = vi.fn(() =>
    Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve(body) }),
  );
  vi.stubGlobal('fetch', fetchMock);
  return fetchMock;
}

function renderSummary(props: { accountId: string | null; week: string; location: string | null }) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <ActivitySummary {...props} />
    </QueryClientProvider>,
  );
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('ActivitySummary', () => {
  it('renders one card per Metric with its label, count and insufficient data badge', async () => {
    stubFetch({ success: true, data: PAYLOAD });

    renderSummary({ accountId: '1', week: '2026-07-20', location: null });

    const calls = await screen.findByRole('article', { name: 'Calls received' });
    expect(within(calls).getByText('17')).toBeInTheDocument();
    expect(within(calls).getByText('Insufficient data')).toBeInTheDocument();
    const leads = screen.getByRole('article', { name: 'Leads created' });
    expect(within(leads).getByText('4')).toBeInTheDocument();
    const appointments = screen.getByRole('article', { name: 'Appointments set' });
    expect(within(appointments).getByText('0')).toBeInTheDocument();
    expect(screen.getAllByRole('article')).toHaveLength(3);
  });

  it('shows the API error message when the summary cannot be loaded', async () => {
    stubFetch({
      success: false,
      message: 'Internal server error.',
      errors: {},
      error_code: 'SERVER_ERROR',
    });

    renderSummary({ accountId: '1', week: '2026-07-20', location: null });

    expect(await screen.findByRole('alert')).toHaveTextContent('Internal server error.');
    expect(screen.queryByRole('article')).not.toBeInTheDocument();
  });

  it('shows a loading state until the summary arrives', async () => {
    stubFetch({ success: true, data: PAYLOAD });

    renderSummary({ accountId: '1', week: '2026-07-20', location: null });

    expect(screen.getByRole('status')).toHaveTextContent('Loading activity…');
    expect(screen.queryByRole('article')).not.toBeInTheDocument();
    await screen.findAllByRole('article');
    expect(screen.queryByRole('status')).not.toBeInTheDocument();
  });

  it('asks for an Account and does not call the API when none is selected', () => {
    const fetchMock = stubFetch({ success: true, data: PAYLOAD });

    renderSummary({ accountId: null, week: '2026-07-20', location: null });

    expect(screen.getByText('Choose an account to see its activity.')).toBeInTheDocument();
    expect(screen.queryByRole('status')).not.toBeInTheDocument();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('says so when the API returns no Metrics', async () => {
    stubFetch({ success: true, data: { ...PAYLOAD, metrics: [] } });

    renderSummary({ accountId: '1', week: '2026-07-20', location: null });

    expect(await screen.findByText('No activity data for this selection.')).toBeInTheDocument();
    expect(screen.queryByRole('article')).not.toBeInTheDocument();
  });
});
