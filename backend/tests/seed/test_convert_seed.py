import csv

from seed.convert_seed import convert

SQL = '''-- comment line
-- accounts
INSERT INTO accounts (id, name, industry, timezone, created_at) VALUES (1, 'Summit, Auto', 'Auto', 'America/Chicago', '2025-05-12 12:00:00');
INSERT INTO accounts (id, name, industry, timezone, created_at) VALUES (2, 'O''Neil Dental', 'Dental', 'UTC', '2025-01-04 12:00:00');

-- activity_events
INSERT INTO activity_events (id, account_id, location, event_type, occurred_at, duration_seconds, outcome) VALUES (1, 1, 'Site A', 'call_received', '2026-02-01 10:57:44', 621, 'missed');
INSERT INTO activity_events (id, account_id, location, event_type, occurred_at, duration_seconds, outcome) VALUES (2, 2, 'Site B', 'lead_created', '2026-02-01 11:00:00', NULL, NULL);
'''


def read_rows(path):
    with path.open(newline='') as handle:
        return list(csv.reader(handle))


def test_convert_writes_accounts_and_activity_events_csvs(tmp_path):
    source = tmp_path / 'seed.txt'
    source.write_text(SQL)

    convert(source, tmp_path)

    assert read_rows(tmp_path / 'accounts.csv') == [
        ['id', 'name', 'industry', 'timezone', 'created_at'],
        ['1', 'Summit, Auto', 'Auto', 'America/Chicago', '2025-05-12 12:00:00'],
        ['2', "O'Neil Dental", 'Dental', 'UTC', '2025-01-04 12:00:00'],
    ]
    assert read_rows(tmp_path / 'activity_events.csv') == [
        ['id', 'account_id', 'location', 'event_type', 'occurred_at', 'duration_seconds', 'outcome'],
        ['1', '1', 'Site A', 'call_received', '2026-02-01 10:57:44', '621', 'missed'],
        ['2', '2', 'Site B', 'lead_created', '2026-02-01 11:00:00', '', ''],
    ]
