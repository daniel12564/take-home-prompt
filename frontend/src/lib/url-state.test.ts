import { describe, expect, it } from 'vitest';

import {
  normalizeWeek,
  parseSelection,
  selectAccount,
  selectLocation,
  selectWeek,
} from './url-state';

describe('url-state', () => {
  it('reads account and location from the search string', () => {
    expect(parseSelection('?account=6&location=Site+B')).toEqual({
      account: '6',
      week: null,
      location: 'Site B',
    });
    expect(parseSelection('')).toEqual({ account: null, week: null, location: null });
    expect(parseSelection('?week=2026-07-13').week).toBe('2026-07-13');
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

  it('stores the chosen week and keeps the other params', () => {
    expect(selectWeek('?account=6&location=Site+B', '2026-07-13')).toBe(
      '?account=6&location=Site+B&week=2026-07-13',
    );
  });

  it('falls back to the default week when the week is missing or invalid', () => {
    expect(normalizeWeek('?account=1')).toBe('?account=1&week=2026-07-20');
    expect(normalizeWeek('?week=2026-07-27&account=1')).toBe('?week=2026-07-20&account=1');
    expect(normalizeWeek('?week=junk')).toBe('?week=2026-07-20');
    expect(normalizeWeek('')).toBe('?week=2026-07-20');
  });

  it('leaves a valid week untouched', () => {
    expect(normalizeWeek('?account=1&week=2026-03-02')).toBe('?account=1&week=2026-03-02');
  });
});
