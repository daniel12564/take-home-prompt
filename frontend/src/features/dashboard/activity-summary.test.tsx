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

  it('shows the per-field validation messages when the location is unknown', async () => {
    stubFetch({
      success: false,
      message: 'Validation failed.',
      errors: { location: ['Unknown location for this account.'] },
      error_code: 'VALIDATION_ERROR',
    });

    renderSummary({ accountId: '1', week: '2026-07-20', location: 'Nowhere' });

    const alert = await screen.findByRole('alert');
    expect(alert).toHaveTextContent('Validation failed.');
    expect(alert).toHaveTextContent('location: Unknown location for this account.');
    expect(screen.queryByRole('article')).not.toBeInTheDocument();
  });

  it('shows every field message and does not repeat a field name the message already starts with', async () => {
    stubFetch({
      success: false,
      message: 'Validation failed.',
      errors: {
        week_start: ['week_start must be a Monday.'],
        location: ['Unknown location for this account.', 'Second problem.'],
      },
      error_code: 'VALIDATION_ERROR',
    });

    renderSummary({ accountId: '1', week: '2026-07-21', location: 'Nowhere' });

    const alert = await screen.findByRole('alert');
    expect(alert).toHaveTextContent('week_start must be a Monday.');
    expect(alert).not.toHaveTextContent('week_start: week_start');
    expect(alert).toHaveTextContent('location: Unknown location for this account.');
    expect(alert).toHaveTextContent('location: Second problem.');
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

function metric(overrides: Record<string, unknown>) {
  return {
    event_type: 'call_received',
    current: 51,
    baseline: 42,
    delta: 9,
    delta_pct: 21.4,
    status: 'typical',
    ...overrides,
  };
}

function payloadWith(metrics: unknown[], baselineWeeksUsed = 8) {
  return { ...PAYLOAD, baseline_weeks_used: baselineWeeksUsed, metrics };
}

describe('ActivitySummary Baseline and Status', () => {
  it('shows the typical value, the difference and its percentage next to the count', async () => {
    stubFetch({ success: true, data: payloadWith([metric({})]) });

    renderSummary({ accountId: '1', week: '2026-07-20', location: null });

    const calls = await screen.findByRole('article', { name: 'Calls received' });
    expect(within(calls).getByText('51')).toBeInTheDocument();
    expect(within(calls).getByText('Typical: 42')).toBeInTheDocument();
    expect(within(calls).getByText('+9 (+21.4%)')).toBeInTheDocument();
    expect(within(calls).getByText('Typical')).toBeInTheDocument();
  });

  it('shows a drop with a minus sign and a fractional Baseline with one decimal', async () => {
    stubFetch({
      success: true,
      data: payloadWith([metric({ current: 2, baseline: 3.5, delta: -1.5, delta_pct: -42.9, status: 'typical' })]),
    });

    renderSummary({ accountId: '1', week: '2026-07-20', location: null });

    const calls = await screen.findByRole('article', { name: 'Calls received' });
    expect(within(calls).getByText('Typical: 3.5')).toBeInTheDocument();
    expect(within(calls).getByText('-1.5 (-42.9%)')).toBeInTheDocument();
  });

  it('shows only the difference when the percentage is undefined', async () => {
    stubFetch({
      success: true,
      data: payloadWith([metric({ current: 3, baseline: 0, delta: 3, delta_pct: null, status: 'above' })]),
    });

    renderSummary({ accountId: '1', week: '2026-07-20', location: null });

    const calls = await screen.findByRole('article', { name: 'Calls received' });
    expect(within(calls).getByText('Typical: 0')).toBeInTheDocument();
    expect(within(calls).getByText('+3')).toBeInTheDocument();
    expect(within(calls).getByText('Above typical')).toBeInTheDocument();
  });

  it('says how many weeks of history the Baseline was computed from', async () => {
    stubFetch({ success: true, data: payloadWith([metric({})], 8) });

    renderSummary({ accountId: '1', week: '2026-07-20', location: null });

    expect(await screen.findByText('Typical values are based on the 8 weeks before this one.')).toBeInTheDocument();
  });

  it('uses the singular for a single week of history', async () => {
    stubFetch({ success: true, data: payloadWith([metric({})], 1) });

    renderSummary({ accountId: '1', week: '2026-07-20', location: null });

    expect(await screen.findByText('Typical values are based on the 1 week before this one.')).toBeInTheDocument();
  });

  it('explains that more weeks of history are needed instead of showing a verdict', async () => {
    stubFetch({
      success: true,
      data: payloadWith(
        [metric({ baseline: null, delta: null, delta_pct: null, status: 'insufficient_data' })],
        3,
      ),
    });

    renderSummary({ accountId: '1', week: '2026-02-23', location: null });

    const calls = await screen.findByRole('article', { name: 'Calls received' });
    expect(within(calls).getByText('Insufficient data')).toBeInTheDocument();
    expect(
      within(calls).getByText('Not enough history yet: more weeks of activity are needed to judge this week.'),
    ).toBeInTheDocument();
    expect(within(calls).queryByText(/Typical:/)).not.toBeInTheDocument();
    expect(within(calls).queryByText(/%\)/)).not.toBeInTheDocument();
    expect(screen.queryByText(/Typical values are based on/)).not.toBeInTheDocument();
  });

  it('says there is no activity at all, not that history is short, when nothing was recorded', async () => {
    stubFetch({
      success: true,
      data: {
        ...payloadWith(
          [metric({ current: 0, baseline: null, delta: null, delta_pct: null, status: 'insufficient_data' })],
          8,
        ),
        insufficient_reason: 'no_events',
      },
    });

    renderSummary({ accountId: '20', week: '2026-07-20', location: null });

    const calls = await screen.findByRole('article', { name: 'Calls received' });
    expect(
      within(calls).getByText(
        'No activity has been recorded for this account yet, so there is nothing to compare against.',
      ),
    ).toBeInTheDocument();
    expect(within(calls).queryByText(/Not enough history yet/)).not.toBeInTheDocument();
  });

  it('names the Location when the selected Location has no activity', async () => {
    stubFetch({
      success: true,
      data: {
        ...payloadWith(
          [metric({ current: 0, baseline: null, delta: null, delta_pct: null, status: 'insufficient_data' })],
          8,
        ),
        location: 'Site A',
        insufficient_reason: 'no_events',
      },
    });

    renderSummary({ accountId: '6', week: '2026-07-20', location: 'Site A' });

    const calls = await screen.findByRole('article', { name: 'Calls received' });
    expect(
      within(calls).getByText(
        'No activity has been recorded for this location yet, so there is nothing to compare against.',
      ),
    ).toBeInTheDocument();
  });

  it('keeps the short history explanation when the API says the history is short', async () => {
    stubFetch({
      success: true,
      data: {
        ...payloadWith(
          [metric({ baseline: null, delta: null, delta_pct: null, status: 'insufficient_data' })],
          2,
        ),
        insufficient_reason: 'short_history',
      },
    });

    renderSummary({ accountId: '1', week: '2026-02-16', location: null });

    const calls = await screen.findByRole('article', { name: 'Calls received' });
    expect(within(calls).getByText(/Not enough history yet/)).toBeInTheDocument();
    expect(within(calls).queryByText(/No activity has been recorded/)).not.toBeInTheDocument();
  });

  it('does not show the insufficient data explanation on a judged card', async () => {
    stubFetch({ success: true, data: payloadWith([metric({})]) });

    renderSummary({ accountId: '1', week: '2026-07-20', location: null });

    await screen.findByRole('article', { name: 'Calls received' });
    expect(screen.queryByText(/Not enough history yet/)).not.toBeInTheDocument();
  });
});
