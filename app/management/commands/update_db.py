from django.core.management.base import BaseCommand

from app.src.update_db import update_all, update_all_for_region


class Command(BaseCommand):
    help = 'Pulls ladder data from the Blizzard API into our database.'

    def add_arguments(self, parser):
        parser.add_argument('--region', help='Region to update')

    def handle(self, *args, **options):
        region = options['region']
        if region not in [None, 'us', 'eu', 'kr']:
            print('Region must be one of: us, eu, kr')
            return
        if region is None:
            print('Updating all regions')
            update_all()
        else:
            print(f'Updating the {region} region')
            update_all_for_region(region)
        print('Updated')
