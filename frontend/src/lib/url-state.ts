import { useCallback, useSyncExternalStore } from 'react';

export interface Selection {
  account: string | null;
  location: string | null;
}

const URL_CHANGE_EVENT = 'urlstatechange';

export function parseSelection(search: string): Selection {
  const params = new URLSearchParams(search);
  return {
    account: params.get('account'),
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

  const setSearch = useCallback((next: string) => {
    if (next === window.location.search) return;
    window.history.pushState(null, '', `${window.location.pathname}${next}`);
    window.dispatchEvent(new Event(URL_CHANGE_EVENT));
  }, []);

  return [search, setSearch] as const;
}
