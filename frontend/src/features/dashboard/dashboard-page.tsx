import { parseSelection, selectAccount, selectLocation, useUrlSearch } from '../../lib/url-state';
import { AccountSelector } from './account-selector';
import { LocationSelector } from './location-selector';

export function DashboardPage() {
  const [search, setSearch] = useUrlSearch();
  const { account, location } = parseSelection(search);

  return (
    <div className='min-h-screen'>
      <header className='border-b border-slate-200 bg-white'>
        <div className='mx-auto flex max-w-5xl flex-wrap items-end gap-4 px-6 py-4'>
          <h1 className='mr-auto text-xl font-semibold text-slate-900'>Relay reporting dashboard</h1>
          <AccountSelector
            value={account}
            onChange={(next) => setSearch(selectAccount(search, next))}
          />
          <LocationSelector
            accountId={account}
            value={location}
            onChange={(next) => setSearch(selectLocation(search, next))}
          />
        </div>
      </header>
      <main className='mx-auto max-w-5xl p-6' />
    </div>
  );
}
