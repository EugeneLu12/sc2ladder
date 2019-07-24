from django.core.management.base import BaseCommand

from app.src.update_db import update_all, update_all_for_region, update_gm_for_region_legacy


class Command(BaseCommand):
    help = 'Pulls ladder data from the Blizzard API into our database.'

    def add_arguments(self, parser):
        parser.add_argument('--region', help='Region to update')
        parser.add_argument('--legacy', action='store_true', help='Whether to use legacy method to update ladder')

    def handle(self, *args, **options):
        region = options['region']
        legacy = options['legacy']
        if region not in [None, 'us', 'eu', 'kr']:
            print('Region must be one of: us, eu, kr')
            return
        if region is None:
            print('Updating all regions')
            update_all()
        else:
            print(f'Updating the {region} region')
            if legacy:
                update_gm_for_region_legacy(region)
            else:
                update_all_for_region(region)
        print('Updated')
