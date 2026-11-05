import { useHealth } from '../../api/health';

export function DashboardPage() {
  const { data, error, isPending } = useHealth();

  return (
    <main className="mx-auto max-w-3xl p-6">
      <h1 className="text-2xl font-semibold text-slate-900">Relay reporting dashboard</h1>
      <section className="mt-6 rounded-lg border border-slate-200 bg-white p-4">
        {isPending && <p className="text-slate-500">Loading…</p>}
        {error && (
          <p role="alert" className="text-red-700">
            {error.message}
          </p>
        )}
        {data && <p className="text-green-700">API status: {data.status}</p>}
      </section>
    </main>
  );
}
