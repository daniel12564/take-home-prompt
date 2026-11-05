import csv
from datetime import datetime, timezone

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import connection, transaction

from accounts.models import Account
from activity.models import ActivityEvent

BATCH_SIZE = 1000


def parse_timestamp(value):
    return datetime.fromisoformat(value).replace(tzinfo=timezone.utc)


def parse_optional(value, cast=str):
    return cast(value) if value != '' else None


def read_rows(path):
    with path.open(newline='') as handle:
        yield from csv.DictReader(handle)


def account_from_row(row):
    return Account(
        id=int(row['id']),
        name=row['name'],
        industry=row['industry'],
        timezone=row['timezone'],
        created_at=parse_timestamp(row['created_at']),
    )


def event_from_row(row):
    return ActivityEvent(
        id=int(row['id']),
        account_id=int(row['account_id']),
        location=row['location'],
        event_type=row['event_type'],
        occurred_at=parse_timestamp(row['occurred_at']),
        duration_seconds=parse_optional(row['duration_seconds'], int),
        outcome=parse_optional(row['outcome']),
    )


def bulk_load(model, rows, build):
    batch = []
    total = 0
    for row in rows:
        batch.append(build(row))
        if len(batch) == BATCH_SIZE:
            model.objects.bulk_create(batch)
            total += len(batch)
            batch = []
    if batch:
        model.objects.bulk_create(batch)
        total += len(batch)
    return total


def reset_sequences():
    statements = connection.ops.sequence_reset_sql(no_style(), [Account, ActivityEvent])
    with connection.cursor() as cursor:
        for statement in statements:
            cursor.execute(statement)


class Command(BaseCommand):
    help = 'Load accounts.csv and activity_events.csv from the seed directory.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Delete all Activity Events and Accounts before loading.',
        )

    def handle(self, *args, **options):
        if Account.objects.exists() and not options['flush']:
            self.stdout.write('Accounts already exist; skipping seed (use --flush to reload).')
            return

        seed_dir = settings.SEED_DIR
        with transaction.atomic():
            if options['flush']:
                ActivityEvent.objects.all().delete()
                Account.objects.all().delete()
            accounts = bulk_load(Account, read_rows(seed_dir / 'accounts.csv'), account_from_row)
            events = bulk_load(
                ActivityEvent, read_rows(seed_dir / 'activity_events.csv'), event_from_row
            )
            reset_sequences()

        self.stdout.write(f'Loaded {accounts} accounts and {events} activity events.')
