import { useCallback, useSyncExternalStore } from 'react';

import { defaultWeek, isSelectableWeek } from './weeks';

export interface Selection {
  account: string | null;
  week: string | null;
  location: string | null;
}

const URL_CHANGE_EVENT = 'urlstatechange';

export function parseSelection(search: string): Selection {
  const params = new URLSearchParams(search);
  return {
    account: params.get('account'),
    week: params.get('week'),
    location: params.get('location'),
  };
}

function toSearch(params: URLSearchParams) {
  const query = params.toString();
  return query ? `?${query}` : '';
}

export function selectAccount(search: string, account: string) {
  const params = new URLSearchParams(search);
  params.delete('location');
  if (account) {
    params.set('account', account);
  } else {
    params.delete('account');
  }
  return toSearch(params);
}

export function selectLocation(search: string, location: string) {
  const params = new URLSearchParams(search);
  if (location) {
    params.set('location', location);
  } else {
    params.delete('location');
  }
  return toSearch(params);
}

export function selectWeek(search: string, week: string) {
  const params = new URLSearchParams(search);
  params.set('week', week);
  return toSearch(params);
}

export function normalizeWeek(search: string) {
  const params = new URLSearchParams(search);
  if (isSelectableWeek(params.get('week'))) return search;
  params.set('week', defaultWeek());
  return toSearch(params);
}

function subscribe(callback: () => void) {
  window.addEventListener('popstate', callback);
  window.addEventListener(URL_CHANGE_EVENT, callback);
  return () => {
    window.removeEventListener('popstate', callback);
    window.removeEventListener(URL_CHANGE_EVENT, callback);
  };
}

function getSearch() {
  return window.location.search;
}

export function useUrlSearch() {
  const search = useSyncExternalStore(subscribe, getSearch);

  const setSearch = useCallback((next: string, options?: { replace?: boolean }) => {
    if (next === window.location.search) return;
    const url = `${window.location.pathname}${next}`;
    if (options?.replace) {
      window.history.replaceState(null, '', url);
    } else {
      window.history.pushState(null, '', url);
    }
    window.dispatchEvent(new Event(URL_CHANGE_EVENT));
  }, []);

  return [search, setSearch] as const;
}
