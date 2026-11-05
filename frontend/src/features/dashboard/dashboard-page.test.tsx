import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { DashboardPage } from './dashboard-page';

const ACCOUNTS = [
  { id: 1, name: 'Summit Auto Group', timezone: 'America/Chicago', location_count: 3 },
  { id: 2, name: 'Harbor Dental Partners', timezone: 'America/New_York', location_count: 1 },
  { id: 20, name: 'Quiet Harbor Spa', timezone: 'America/Los_Angeles', location_count: 0 },
];

const LOCATIONS: Record<string, string[]> = {
  '1': ['East', 'North', 'South'],
  '2': ['Site A'],
  '20': [],
};

function summaryBody(accountId: string, location: string | null) {
  const current = location ? 3 : 9;
  return {
    account_id: Number(accountId),
    week_start: '2026-07-20',
    week_end: '2026-07-26',
    location,
    baseline_weeks_used: 0,
    metrics: ['call_received', 'lead_created', 'appointment_set'].map((event_type) => ({
      event_type,
      current,
      baseline: null,
      delta: null,
      delta_pct: null,
      status: 'insufficient_data',
    })),
  };
}

function stubApi() {
  const fetchMock = vi.fn((url: string) => {
    const locationsMatch = url.match(/\/accounts\/(\d+)\/locations\/$/);
    const summaryMatch = url.match(/\/accounts\/(\d+)\/dashboard\/activity-summary\/\?(.*)$/);
    let body: unknown;
    if (summaryMatch) {
      const params = new URLSearchParams(summaryMatch[2]);
      body = { success: true, data: summaryBody(summaryMatch[1], params.get('location')) };
    } else if (url.endsWith('/accounts/')) {
      body = { success: true, data: ACCOUNTS };
    } else if (locationsMatch) {
      body = { success: true, data: LOCATIONS[locationsMatch[1]] };
    } else {
      body = {
        success: false,
        message: 'Not found.',
        errors: {},
        error_code: 'NOT_FOUND',
      };
    }
    return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve(body) });
  });
  vi.stubGlobal('fetch', fetchMock);
  return fetchMock;
}

function renderPage(search = '') {
  window.history.replaceState(null, '', `/${search}`);
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <DashboardPage />
    </QueryClientProvider>,
  );
}

function accountSelect() {
  return screen.getByLabelText('Account') as HTMLSelectElement;
}

function locationSelect() {
  return screen.getByLabelText('Location') as HTMLSelectElement;
}

describe('DashboardPage header selectors', () => {
  beforeEach(() => {
    stubApi();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('lists every Account with its name and Location count', async () => {
    renderPage();

    expect(
      await screen.findByRole('option', { name: 'Summit Auto Group (3 locations)' }),
    ).toBeInTheDocument();
    expect(screen.getByRole('option', { name: 'Harbor Dental Partners (1 location)' })).toBeInTheDocument();
    expect(screen.getByRole('option', { name: 'Quiet Harbor Spa (0 locations)' })).toBeInTheDocument();
  });

  it('stores the chosen Account in the URL and offers its Locations', async () => {
    renderPage();
    await screen.findByRole('option', { name: 'Summit Auto Group (3 locations)' });

    fireEvent.change(accountSelect(), { target: { value: '1' } });

    expect(window.location.search).toBe('?week=2026-07-20&account=1');
    expect(await screen.findByRole('option', { name: 'North' })).toBeInTheDocument();
    expect(screen.getByRole('option', { name: 'All locations' })).toBeInTheDocument();
    const names = Array.from(locationSelect().options).map((option) => option.text);
    expect(names).toEqual(['All locations', 'East', 'North', 'South']);
  });

  it('restores both selections from the URL on load', async () => {
    renderPage('?account=1&location=North');

    await waitFor(() => expect(locationSelect().value).toBe('North'));
    expect(accountSelect().value).toBe('1');
  });

  it('stores the chosen Location in the URL and clears it with All locations', async () => {
    renderPage('?account=1');
    await screen.findByRole('option', { name: 'South' });

    fireEvent.change(locationSelect(), { target: { value: 'South' } });
    expect(window.location.search).toBe('?account=1&week=2026-07-20&location=South');

    fireEvent.change(locationSelect(), { target: { value: '' } });
    expect(window.location.search).toBe('?account=1&week=2026-07-20');
  });

  it('clears the Location when the Account changes', async () => {
    renderPage('?account=1&week=2026-07-20&location=North');
    await waitFor(() => expect(locationSelect().value).toBe('North'));

    fireEvent.change(accountSelect(), { target: { value: '2' } });

    expect(window.location.search).toBe('?account=2&week=2026-07-20');
    await waitFor(() => expect(locationSelect().value).toBe(''));
    expect(await screen.findByRole('option', { name: 'Site A' })).toBeInTheDocument();
  });

  it('keeps other URL params when the Account changes', async () => {
    renderPage('?account=1&week=2026-07-20&location=North');
    await screen.findByRole('option', { name: 'Harbor Dental Partners (1 location)' });

    fireEvent.change(accountSelect(), { target: { value: '2' } });

    expect(window.location.search).toBe('?account=2&week=2026-07-20');
  });

  it('disables the Location selector with an explanation when the Account has no Locations', async () => {
    renderPage('?account=20');

    expect(await screen.findByText('This account has no locations yet.')).toBeInTheDocument();
    expect(locationSelect()).toBeDisabled();
  });

  it('disables the Location selector until an Account is chosen', async () => {
    renderPage();
    await screen.findByRole('option', { name: 'Summit Auto Group (3 locations)' });

    expect(locationSelect()).toBeDisabled();
    expect(screen.getByText('Choose an account first.')).toBeInTheDocument();
  });

  it('shows the API error message when the Accounts cannot be loaded', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        json: () =>
          Promise.resolve({
            success: false,
            message: 'Internal server error.',
            errors: {},
            error_code: 'SERVER_ERROR',
          }),
      }),
    );

    renderPage();

    expect(await screen.findByRole('alert')).toHaveTextContent('Internal server error.');
  });
});

function weekSelect() {
  return screen.getByLabelText('Week') as HTMLSelectElement;
}

describe('DashboardPage week picker', () => {
  beforeEach(() => {
    stubApi();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('lists the complete weeks newest first with readable labels', async () => {
    renderPage();

    const labels = Array.from(weekSelect().options).map((option) => option.text);
    expect(labels).toHaveLength(25);
    expect(labels[0]).toBe('Jul 20 – Jul 26, 2026');
    expect(labels[1]).toBe('Jul 13 – Jul 19, 2026');
    expect(labels[24]).toBe('Feb 2 – Feb 8, 2026');
    expect(screen.queryByRole('option', { name: /Jul 27/ })).not.toBeInTheDocument();
  });

  it('opens on the default week and writes it to the URL when week is missing', async () => {
    renderPage('?account=1');

    await waitFor(() => expect(window.location.search).toBe('?account=1&week=2026-07-20'));
    expect(weekSelect().value).toBe('2026-07-20');
  });

  it.each(['2026-07-27', '2026-07-21', '2025-01-06', 'junk'])(
    'falls back to the default week and fixes the URL when week is %s',
    async (week) => {
      renderPage(`?account=1&week=${week}`);

      await waitFor(() => expect(window.location.search).toBe('?account=1&week=2026-07-20'));
      expect(weekSelect().value).toBe('2026-07-20');
    },
  );

  it('keeps a valid week from the URL', async () => {
    renderPage('?account=1&week=2026-03-02');

    expect(weekSelect().value).toBe('2026-03-02');
    expect(window.location.search).toBe('?account=1&week=2026-03-02');
  });

  it('stores the chosen week in the URL', async () => {
    renderPage('?account=1');

    fireEvent.change(weekSelect(), { target: { value: '2026-07-13' } });

    expect(window.location.search).toBe('?account=1&week=2026-07-13');
    expect(weekSelect().value).toBe('2026-07-13');
  });

  it('keeps the selected week and drops the Location when the Account changes', async () => {
    renderPage('?account=1&week=2026-05-04&location=North');
    await screen.findByRole('option', { name: 'Harbor Dental Partners (1 location)' });

    fireEvent.change(accountSelect(), { target: { value: '2' } });

    expect(window.location.search).toBe('?account=2&week=2026-05-04');
    expect(weekSelect().value).toBe('2026-05-04');
  });
});

function summaryCalls(fetchMock: ReturnType<typeof stubApi>) {
  return fetchMock.mock.calls
    .map(([url]) => String(url))
    .filter((url) => url.includes('/dashboard/activity-summary/'));
}

describe('DashboardPage activity summary', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('asks for an Account instead of fetching when none is selected', async () => {
    const fetchMock = stubApi();
    renderPage();

    expect(await screen.findByText('Choose an account to see its activity.')).toBeInTheDocument();
    expect(summaryCalls(fetchMock)).toEqual([]);
  });

  it('renders the Metric cards for the selected Account, week and Location', async () => {
    const fetchMock = stubApi();
    renderPage('?account=1&week=2026-07-13&location=North');

    const calls = await screen.findByRole('article', { name: 'Calls received' });
    expect(calls).toHaveTextContent('3');
    expect(summaryCalls(fetchMock)).toEqual([
      '/api/v1/accounts/1/dashboard/activity-summary/?week_start=2026-07-13&location=North',
    ]);
  });

  it('omits the Location parameter for the whole Account', async () => {
    const fetchMock = stubApi();
    renderPage('?account=1');

    expect(await screen.findByRole('article', { name: 'Calls received' })).toHaveTextContent('9');
    expect(summaryCalls(fetchMock)).toEqual([
      '/api/v1/accounts/1/dashboard/activity-summary/?week_start=2026-07-20',
    ]);
  });

  it('refetches when the week changes', async () => {
    const fetchMock = stubApi();
    renderPage('?account=1');
    await screen.findByRole('article', { name: 'Calls received' });

    fireEvent.change(weekSelect(), { target: { value: '2026-07-13' } });

    await waitFor(() =>
      expect(summaryCalls(fetchMock)).toContain(
        '/api/v1/accounts/1/dashboard/activity-summary/?week_start=2026-07-13',
      ),
    );
  });

  it('refetches when the Location changes', async () => {
    const fetchMock = stubApi();
    renderPage('?account=1');
    await screen.findByRole('option', { name: 'South' });

    fireEvent.change(locationSelect(), { target: { value: 'South' } });

    expect(await screen.findByRole('article', { name: 'Calls received' })).toHaveTextContent('3');
    expect(summaryCalls(fetchMock)).toContain(
      '/api/v1/accounts/1/dashboard/activity-summary/?week_start=2026-07-20&location=South',
    );
  });

  it('refetches for the new Account when the Account changes', async () => {
    const fetchMock = stubApi();
    renderPage('?account=1');
    await screen.findByRole('option', { name: 'Harbor Dental Partners (1 location)' });

    fireEvent.change(accountSelect(), { target: { value: '2' } });

    await waitFor(() =>
      expect(summaryCalls(fetchMock)).toContain(
        '/api/v1/accounts/2/dashboard/activity-summary/?week_start=2026-07-20',
      ),
    );
  });
});
