import { useEffect } from 'react';

import {
  normalizeWeek,
  parseSelection,
  selectAccount,
  selectLocation,
  selectWeek,
  useUrlSearch,
} from '../../lib/url-state';
import { defaultWeek, isSelectableWeek } from '../../lib/weeks';
import { AccountSelector } from './account-selector';
import { LocationSelector } from './location-selector';
import { WeekPicker } from './week-picker';

export function DashboardPage() {
  const [search, setSearch] = useUrlSearch();
  const { account, week, location } = parseSelection(search);

  useEffect(() => {
    setSearch(normalizeWeek(search), { replace: true });
  }, [search, setSearch]);

  return (
    <div className='min-h-screen'>
      <header className='border-b border-slate-200 bg-white'>
        <div className='mx-auto flex max-w-5xl flex-wrap items-end gap-4 px-6 py-4'>
          <h1 className='mr-auto text-xl font-semibold text-slate-900'>Relay reporting dashboard</h1>
          <AccountSelector
            value={account}
            onChange={(next) => setSearch(selectAccount(search, next))}
          />
          <WeekPicker
            value={isSelectableWeek(week) ? week : defaultWeek()}
            onChange={(next) => setSearch(selectWeek(search, next))}
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
