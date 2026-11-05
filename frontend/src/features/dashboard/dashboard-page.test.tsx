import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { DashboardPage } from './dashboard-page';

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <DashboardPage />
    </QueryClientProvider>,
  );
}

function stubFetch(status: number, body: unknown) {
  const fetchMock = vi.fn().mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    json: () => Promise.resolve(body),
  });
  vi.stubGlobal('fetch', fetchMock);
  return fetchMock;
}

describe('DashboardPage', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('shows loading, then the API status from the success envelope', async () => {
    stubFetch(200, { success: true, data: { status: 'ok' } });

    renderPage();

    expect(screen.getByText(/loading/i)).toBeInTheDocument();
    expect(await screen.findByText(/api status: ok/i)).toBeInTheDocument();
  });

  it('shows the error message from the failure envelope', async () => {
    stubFetch(500, {
      success: false,
      message: 'Internal server error.',
      errors: {},
      error_code: 'SERVER_ERROR',
    });

    renderPage();

    expect(await screen.findByRole('alert')).toHaveTextContent('Internal server error.');
  });
});
