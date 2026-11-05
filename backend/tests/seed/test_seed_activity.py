from datetime import datetime, timezone
from io import StringIO

import pytest
from django.core.management import call_command

from accounts.models import Account
from activity.models import ActivityEvent

ACCOUNTS_CSV = '''id,name,industry,timezone,created_at
7,Seven Co,Dental,America/Phoenix,2025-01-07 12:00:00
9,Nine Co,Fitness,UTC,2025-05-24 12:00:00
'''
EVENTS_CSV = '''id,account_id,location,event_type,occurred_at,duration_seconds,outcome
41,7,Site A,call_received,2026-02-01 10:57:44,621,missed
42,7,Site B,lead_created,2026-02-01 11:00:00,,open
43,9,Site A,appointment_set,2026-02-02 08:30:00,,
'''


@pytest.fixture
def seed_dir(tmp_path, settings):
    (tmp_path / 'accounts.csv').write_text(ACCOUNTS_CSV)
    (tmp_path / 'activity_events.csv').write_text(EVENTS_CSV)
    settings.SEED_DIR = tmp_path
    return tmp_path


def run_seed(*args):
    out = StringIO()
    call_command('seed_activity', *args, stdout=out)
    return out.getvalue()


@pytest.mark.django_db
def test_seed_loads_csvs_preserving_ids_and_nulls(seed_dir):
    run_seed()

    assert list(Account.objects.order_by('id').values_list('id', 'name', 'timezone')) == [
        (7, 'Seven Co', 'America/Phoenix'),
        (9, 'Nine Co', 'UTC'),
    ]
    assert Account.objects.get(pk=7).created_at == datetime(2025, 1, 7, 12, tzinfo=timezone.utc)
    first, second, third = ActivityEvent.objects.order_by('id')
    assert (first.id, first.account_id, first.location, first.event_type) == (
        41, 7, 'Site A', 'call_received'
    )
    assert first.occurred_at == datetime(2026, 2, 1, 10, 57, 44, tzinfo=timezone.utc)
    assert (first.duration_seconds, first.outcome) == (621, 'missed')
    assert (second.duration_seconds, second.outcome) == (None, 'open')
    assert (third.duration_seconds, third.outcome) == (None, None)


@pytest.mark.django_db
def test_seed_resets_sequences_so_new_rows_do_not_collide(seed_dir):
    run_seed()

    account = Account.objects.create(name='New', industry='x', timezone='UTC')
    event = ActivityEvent.objects.create(
        account=account,
        location='Site Z',
        event_type='call_received',
        occurred_at=datetime(2026, 3, 1, tzinfo=timezone.utc),
    )

    assert account.id == 10
    assert event.id == 44


@pytest.mark.django_db
def test_seed_skips_when_accounts_already_exist(seed_dir):
    run_seed()
    output = run_seed()

    assert Account.objects.count() == 2
    assert ActivityEvent.objects.count() == 3
    assert 'skipping' in output.lower()


@pytest.mark.django_db
def test_seed_flush_reloads_from_the_csvs(seed_dir):
    run_seed()
    ActivityEvent.objects.filter(pk=41).delete()
    Account.objects.create(name='Extra', industry='x', timezone='UTC')

    run_seed('--flush')

    assert list(Account.objects.order_by('id').values_list('id', flat=True)) == [7, 9]
    assert list(ActivityEvent.objects.order_by('id').values_list('id', flat=True)) == [41, 42, 43]
