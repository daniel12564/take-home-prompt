'''One-off converter: seed.txt (SQL INSERT statements) -> accounts.csv + activity_events.csv.

Usage (from backend/): python seed/convert_seed.py
An empty CSV cell means NULL.
'''
import csv
import re
import sys
from pathlib import Path

SEED_DIR = Path(__file__).resolve().parent
INSERT_RE = re.compile(r'^INSERT INTO (\w+) \(([^)]*)\) VALUES \((.*)\);\s*$')
TABLES = ('accounts', 'activity_events')


def parse_values(raw):
    values = []
    position = 0
    while position < len(raw):
        if raw[position] == "'":
            position += 1
            chars = []
            while True:
                if raw[position] == "'":
                    if raw[position + 1:position + 2] == "'":
                        chars.append("'")
                        position += 2
                        continue
                    position += 1
                    break
                chars.append(raw[position])
                position += 1
            values.append(''.join(chars))
        else:
            end = raw.find(',', position)
            end = len(raw) if end == -1 else end
            token = raw[position:end].strip()
            values.append('' if token.upper() == 'NULL' else token)
            position = end
        if raw[position:position + 2] == ', ':
            position += 2
        elif position < len(raw):
            raise ValueError(f'Unexpected content in values: {raw!r}')
    return values


def convert(source, out_dir):
    columns = {}
    rows = {table: [] for table in TABLES}
    for line in Path(source).read_text().splitlines():
        match = INSERT_RE.match(line)
        if not match:
            continue
        table, column_list, raw_values = match.groups()
        if table not in rows:
            raise ValueError(f'Unexpected table {table!r}')
        columns.setdefault(table, [name.strip() for name in column_list.split(',')])
        values = parse_values(raw_values)
        if len(values) != len(columns[table]):
            raise ValueError(f'Column mismatch in: {line[:120]}')
        rows[table].append(values)

    for table in TABLES:
        with (Path(out_dir) / f'{table}.csv').open('w', newline='') as handle:
            writer = csv.writer(handle, lineterminator='\n')
            writer.writerow(columns[table])
            writer.writerows(rows[table])
    return {table: len(rows[table]) for table in TABLES}


if __name__ == '__main__':
    counts = convert(SEED_DIR / 'seed.txt', SEED_DIR)
    sys.stdout.write(f'Wrote {counts}\n')
