from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Load the activity seed data (stub until the models and CSVs land).'

    def handle(self, *args, **options):
        self.stdout.write('seed_activity: nothing to load yet.')
