// Mirrors DASHBOARD_REFERENCE_DATE and DASHBOARD_DATA_START_DATE in the API settings.
const REFERENCE_DATE = '2026-07-27';
const FIRST_WEEK = '2026-02-02';

const DAY_MS = 24 * 60 * 60 * 1000;
const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

function toUtc(day: string) {
  return new Date(`${day}T00:00:00Z`).getTime();
}

function toIso(time: number) {
  return new Date(time).toISOString().slice(0, 10);
}

export function defaultWeek() {
  const reference = new Date(toUtc(REFERENCE_DATE));
  const sinceMonday = (reference.getUTCDay() + 6) % 7;
  return toIso(reference.getTime() - (sinceMonday + 7) * DAY_MS);
}

export function selectableWeeks() {
  const weeks: string[] = [];
  for (let time = toUtc(defaultWeek()); time >= toUtc(FIRST_WEEK); time -= 7 * DAY_MS) {
    weeks.push(toIso(time));
  }
  return weeks;
}

export function isSelectableWeek(week: string | null): week is string {
  return week !== null && selectableWeeks().includes(week);
}

function shortDate(time: number) {
  const date = new Date(time);
  return `${MONTHS[date.getUTCMonth()]} ${date.getUTCDate()}`;
}

export function weekLabel(week: string) {
  const monday = toUtc(week);
  const sunday = monday + 6 * DAY_MS;
  return `${shortDate(monday)} – ${shortDate(sunday)}, ${new Date(sunday).getUTCFullYear()}`;
}
