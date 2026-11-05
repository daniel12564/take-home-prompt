import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen, within } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { AttentionList } from './attention-list';

const NO_ACTIVITY = {
  scope: 'location',
  location: 'South',
  kind: 'no_activity',
  event_types: ['call_received', 'lead_created', 'appointment_set'],
  direction: 'below',
  severity: 'critical',
  current: 0,
  baseline: null,
  delta_pct: null,
  affected_locations: null,
  total_locations: null,
  concentrated_on: null,
  explanation:
    'South recorded no calls, leads or appointments this week; it is normally active.',
};

const SURGE = {
  scope: 'location',
  location: 'North',
  kind: 'metric',
  event_types: ['call_received'],
  direction: 'above',
  severity: 'warning',
  current: 11,
  baseline: 5,
  delta_pct: 120,
  affected_locations: null,
  total_locations: null,
  concentrated_on: null,
  explanation: 'North received 11 calls this week; it typically receives about 5.',
};

const DROP = {
  ...SURGE,
  location: 'East',
  direction: 'below',
  severity: 'critical',
  current: 0,
  delta_pct: -100,
  explanation: 'East received 0 calls this week; it typically receives about 5.',
};

const ACCOUNT_WIDE = {
  scope: 'account',
  location: null,
  kind: 'metric',
  event_types: ['call_received', 'lead_created', 'appointment_set'],
  direction: 'above',
  severity: 'critical',
  current: 529,
  baseline: 41,
  delta_pct: 1190.2,
  affected_locations: 15,
  total_locations: 15,
  concentrated_on: '2026-06-03',
  affected_by_metric: { call_received: 15, lead_created: 15, appointment_set: 14 },
  explanation:
    'Calls, leads and appointments were far above typical at 14 to 15 of 15 locations (529 calls vs about 41). Most of this week\'s events happened on Wed 3 Jun.',
};

function payload(findings: unknown[], insufficientReason: string | null = null) {
  return {
    account_id: 1,
    week_start: '2026-07-20',
    week_end: '2026-07-26',
    insufficient_reason: insufficientReason,
    findings,
  };
}

function stubFetch(body: unknown) {
  const fetchMock = vi.fn(() =>
    Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve(body) }),
  );
  vi.stubGlobal('fetch', fetchMock);
  return fetchMock;
}

function renderList(props: { accountId: string | null; week: string }) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <AttentionList {...props} />
    </QueryClientProvider>,
  );
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('AttentionList', () => {
  it('says nothing needs attention when there are no Findings', async () => {
    stubFetch({ success: true, data: payload([]) });

    renderList({ accountId: '1', week: '2026-07-20' });

    expect(await screen.findByText('Nothing needs attention this week.')).toBeInTheDocument();
    expect(screen.queryByRole('listitem')).not.toBeInTheDocument();
  });

  it('explains that there is not enough history instead of claiming nothing needs attention', async () => {
    stubFetch({ success: true, data: payload([], 'short_history') });

    renderList({ accountId: '1', week: '2026-07-20' });

    expect(
      await screen.findByText(
        'Not enough history yet: more weeks of activity are needed to tell what needs attention this week.',
      ),
    ).toBeInTheDocument();
    expect(screen.queryByText('Nothing needs attention this week.')).not.toBeInTheDocument();
  });

  it('explains that an Account with no activity has nothing to compare against', async () => {
    stubFetch({ success: true, data: payload([], 'no_events') });

    renderList({ accountId: '1', week: '2026-07-20' });

    expect(
      await screen.findByText(
        'No activity has been recorded for this account yet, so there is nothing to compare against.',
      ),
    ).toBeInTheDocument();
    expect(screen.queryByText('Nothing needs attention this week.')).not.toBeInTheDocument();
  });

  it('shows a loading state until the list arrives', async () => {
    stubFetch({ success: true, data: payload([]) });

    renderList({ accountId: '1', week: '2026-07-20' });

    expect(screen.getByRole('status')).toHaveTextContent('Loading findings…');
    await screen.findByText('Nothing needs attention this week.');
    expect(screen.queryByRole('status')).not.toBeInTheDocument();
  });

  it('shows the API error message when the list cannot be loaded', async () => {
    stubFetch({
      success: false,
      message: 'Internal server error.',
      errors: {},
      error_code: 'SERVER_ERROR',
    });

    renderList({ accountId: '1', week: '2026-07-20' });

    expect(await screen.findByRole('alert')).toHaveTextContent('Internal server error.');
    expect(screen.queryByText('Nothing needs attention this week.')).not.toBeInTheDocument();
  });

  it('shows the per-field validation messages when the week is rejected', async () => {
    stubFetch({
      success: false,
      message: 'Validation failed.',
      errors: { week_start: ['week_start must be a Monday.'] },
      error_code: 'VALIDATION_ERROR',
    });

    renderList({ accountId: '1', week: '2026-07-21' });

    const alert = await screen.findByRole('alert');
    expect(alert).toHaveTextContent('Validation failed.');
    expect(alert).toHaveTextContent('week_start must be a Monday.');
    expect(screen.queryByText('Nothing needs attention this week.')).not.toBeInTheDocument();
  });

  it('asks for an Account and does not call the API when none is selected', () => {
    const fetchMock = stubFetch({ success: true, data: payload([]) });

    renderList({ accountId: null, week: '2026-07-20' });

    expect(screen.getByText('Choose an account to see what needs attention.')).toBeInTheDocument();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('renders a critical card before a warning card, in the order the API ranks them', async () => {
    stubFetch({ success: true, data: payload([NO_ACTIVITY, SURGE]) });

    renderList({ accountId: '1', week: '2026-07-20' });

    const cards = await screen.findAllByRole('listitem');
    expect(cards).toHaveLength(2);
    expect(within(cards[0]).getByText('South')).toBeInTheDocument();
    expect(within(cards[0]).getByText('Critical')).toBeInTheDocument();
    expect(within(cards[1]).getByText('North')).toBeInTheDocument();
    expect(within(cards[1]).getByText('Warning')).toBeInTheDocument();
  });

  it('words a no-activity Finding as a silent Location with its explanation', async () => {
    stubFetch({ success: true, data: payload([NO_ACTIVITY]) });

    renderList({ accountId: '1', week: '2026-07-20' });

    const card = await screen.findByRole('listitem');
    expect(within(card).getByText('No activity')).toBeInTheDocument();
    expect(within(card).getByText(NO_ACTIVITY.explanation)).toBeInTheDocument();
    expect(within(card).queryByText(/Typical/)).not.toBeInTheDocument();
  });

  it('words a surge neutrally with this week and typical values', async () => {
    stubFetch({ success: true, data: payload([SURGE]) });

    renderList({ accountId: '1', week: '2026-07-20' });

    const card = await screen.findByRole('listitem');
    expect(within(card).getByText('Calls received')).toBeInTheDocument();
    expect(within(card).getByText('Above typical')).toBeInTheDocument();
    expect(within(card).getByText('This week: 11')).toBeInTheDocument();
    expect(within(card).getByText('Typical: 5')).toBeInTheDocument();
    expect(within(card).getByText('+120%')).toBeInTheDocument();
    expect(within(card).getByText(SURGE.explanation)).toBeInTheDocument();
  });

  it('words a drop as a drop', async () => {
    stubFetch({ success: true, data: payload([DROP]) });

    renderList({ accountId: '1', week: '2026-07-20' });

    const card = await screen.findByRole('listitem');
    expect(within(card).getByText('Dropped')).toBeInTheDocument();
    expect(within(card).getByText('This week: 0')).toBeInTheDocument();
    expect(within(card).getByText('-100%')).toBeInTheDocument();
  });

  it('gives each Severity its own styling', async () => {
    stubFetch({ success: true, data: payload([NO_ACTIVITY, SURGE]) });

    renderList({ accountId: '1', week: '2026-07-20' });

    const [critical, warning] = await screen.findAllByRole('listitem');
    expect(critical).toHaveAttribute('data-severity', 'critical');
    expect(warning).toHaveAttribute('data-severity', 'warning');
    expect(critical.className).not.toBe(warning.className);
  });

  it('styles a critical surge as amber, never as the red problem styling, and keeps its Severity', async () => {
    const criticalSurge = { ...SURGE, severity: 'critical', current: 12, delta_pct: 140 };
    stubFetch({ success: true, data: payload([ACCOUNT_WIDE, criticalSurge, NO_ACTIVITY]) });

    renderList({ accountId: '1', week: '2026-06-01' });

    const [accountWide, surge, silent] = await screen.findAllByRole('listitem');
    for (const card of [accountWide, surge]) {
      expect(card).toHaveAttribute('data-severity', 'critical');
      const badge = within(card).getByText('Critical');
      expect(badge.className).toContain('amber');
      expect(badge.className).not.toContain('red');
      expect(card.className).not.toContain('red');
    }
    expect(surge.className).toContain('amber');
    expect(within(silent).getByText('Critical').className).toContain('red');
    expect(silent.className).toContain('red');
  });

  it('renders an Account-wide card above the per-Location cards', async () => {
    stubFetch({ success: true, data: payload([ACCOUNT_WIDE, NO_ACTIVITY, SURGE]) });

    renderList({ accountId: '1', week: '2026-06-01' });

    const cards = await screen.findAllByRole('listitem');
    expect(cards).toHaveLength(3);
    expect(cards[0]).toHaveAttribute('data-scope', 'account');
    expect(within(cards[0]).getByText('Account-wide')).toBeInTheDocument();
    expect(within(cards[0]).getByText(ACCOUNT_WIDE.explanation)).toBeInTheDocument();
    expect(cards[1]).toHaveAttribute('data-scope', 'location');
    expect(within(cards[1]).getByText('South')).toBeInTheDocument();
    expect(within(cards[2]).getByText('North')).toBeInTheDocument();
  });

  it('shows how many locations an Account-wide Finding affected and which Metrics', async () => {
    stubFetch({ success: true, data: payload([ACCOUNT_WIDE]) });

    renderList({ accountId: '1', week: '2026-06-01' });

    const card = await screen.findByRole('listitem');
    expect(within(card).getByText('15 of 15 locations')).toBeInTheDocument();
    expect(within(card).getByText('Calls received: 15 of 15')).toBeInTheDocument();
    expect(within(card).getByText('Leads created: 15 of 15')).toBeInTheDocument();
    expect(within(card).getByText('Appointments set: 14 of 15')).toBeInTheDocument();
    expect(within(card).getByText('Above typical')).toBeInTheDocument();
    expect(within(card).queryByText(/^This week:/)).not.toBeInTheDocument();
  });

  it('calls out the day an Account-wide Finding was concentrated on', async () => {
    stubFetch({ success: true, data: payload([ACCOUNT_WIDE]) });

    renderList({ accountId: '1', week: '2026-06-01' });

    const card = await screen.findByRole('listitem');
    expect(within(card).getByText('Concentrated on Wed 3 Jun')).toBeInTheDocument();
  });

  it('shows no day callout when the week was not concentrated', async () => {
    stubFetch({
      success: true,
      data: payload([{ ...ACCOUNT_WIDE, concentrated_on: null }]),
    });

    renderList({ accountId: '1', week: '2026-06-01' });

    const card = await screen.findByRole('listitem');
    expect(within(card).queryByText(/Concentrated on/)).not.toBeInTheDocument();
  });

  it('styles an Account-wide card differently from a per-Location card', async () => {
    stubFetch({ success: true, data: payload([ACCOUNT_WIDE, NO_ACTIVITY]) });

    renderList({ accountId: '1', week: '2026-06-01' });

    const [account, location] = await screen.findAllByRole('listitem');
    expect(account.className).not.toBe(location.className);
  });
});
