import { describe, expect, it } from 'vitest';

import { parseSelection, selectAccount, selectLocation } from './url-state';

describe('url-state', () => {
  it('reads account and location from the search string', () => {
    expect(parseSelection('?account=6&location=Site+B')).toEqual({
      account: '6',
      location: 'Site B',
    });
    expect(parseSelection('')).toEqual({ account: null, location: null });
  });

  it('removes the location when the account changes and keeps other params', () => {
    expect(selectAccount('?account=1&week=2026-07-20&location=North', '2')).toBe(
      '?account=2&week=2026-07-20',
    );
  });

  it('encodes a location with spaces and removes it for all locations', () => {
    expect(selectLocation('?account=6', 'Site B')).toBe('?account=6&location=Site+B');
    expect(selectLocation('?account=6&location=Site+B', '')).toBe('?account=6');
  });
});
