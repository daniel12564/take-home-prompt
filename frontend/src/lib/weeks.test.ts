import { describe, expect, it } from 'vitest';

import { defaultWeek, isSelectableWeek, selectableWeeks, weekLabel } from './weeks';

describe('weeks', () => {
  it('defaults to the last complete week before the Reference Date', () => {
    expect(defaultWeek()).toBe('2026-07-20');
  });

  it('lists every complete week newest first, never the in-progress week', () => {
    const weeks = selectableWeeks();

    expect(weeks).toHaveLength(25);
    expect(weeks[0]).toBe('2026-07-20');
    expect(weeks[1]).toBe('2026-07-13');
    expect(weeks[weeks.length - 1]).toBe('2026-02-02');
    expect(weeks).not.toContain('2026-07-27');
  });

  it('accepts only listed weeks', () => {
    expect(isSelectableWeek('2026-02-02')).toBe(true);
    expect(isSelectableWeek('2026-07-20')).toBe(true);
    expect(isSelectableWeek('2026-07-27')).toBe(false);
    expect(isSelectableWeek('2026-01-26')).toBe(false);
    expect(isSelectableWeek('2026-07-21')).toBe(false);
    expect(isSelectableWeek('not-a-date')).toBe(false);
    expect(isSelectableWeek(null)).toBe(false);
  });

  it('labels a week with its Monday and Sunday', () => {
    expect(weekLabel('2026-07-20')).toBe('Jul 20 – Jul 26, 2026');
    expect(weekLabel('2026-02-02')).toBe('Feb 2 – Feb 8, 2026');
    expect(weekLabel('2026-03-30')).toBe('Mar 30 – Apr 5, 2026');
  });
});
