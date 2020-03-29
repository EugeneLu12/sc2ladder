from django.core.management.base import BaseCommand

from app.src.update_db import (
    update_ranks,
    update_gm_for_region_legacy,
    update_public_ladders,
    update_public_players,
)


class Command(BaseCommand):
    help = "Pulls ladder data from the Blizzard API into our database."

    def add_arguments(self, parser):
        parser.add_argument("--region", help="Region to update")
        parser.add_argument("--league", help="League to update")
        parser.add_argument(
            "--legacy",
            action="store_true",
            help="Whether to use legacy method to update ladder",
        )
        parser.add_argument(
            "--public",
            action="store_true",
            help="Use public endpoints only to update ladder",
        )
        parser.add_argument(
            "--ladders",
            action="store_true",
            help="Include to update ladders stored in database.",
        )
        parser.add_argument(
            "--players",
            action="store_true",
            help="Include to update players stored in database.",
        )

    def handle(self, *args, **options):
        region = options["region"]
        legacy = options["legacy"]
        public = options["public"]
        league = options["league"]
        ladders = options["ladders"]
        players = options["players"]

        if region not in [None, "us", "eu", "kr"]:
            print("Region must be one of: us, eu, kr")
            return
        print(f"Updating the {region} region {league} league")
        if public:
            if ladders:
                update_public_ladders(region, league)
            if players:
                update_public_players(region, league)
        else:
            if legacy:
                update_gm_for_region_legacy(region)
            else:
                update_ranks(region, league)
