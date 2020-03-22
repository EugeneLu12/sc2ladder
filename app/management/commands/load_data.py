import json

from django.core.management.base import BaseCommand

from app.models.identity import Identity
from app.models.player import Player


class Command(BaseCommand):
    help = "Loads aliases to Identity table and links to a Player object"

    def add_arguments(self, parser):
        parser.add_argument("--filename", help="Filename to load from")

    def handle(self, *args, **options):
        filename = options["filename"]
        with open(filename) as file:
            player_list = json.load(file)

        for player in player_list:
            profile_id = player["profile_id"]
            realm = player["realm"]
            region = player["region"]
            alias = player.get("alias")
            game_link = player.get("game_link")
            if alias:
                ident, created = Identity.objects.get_or_create(alias=alias)
                print(ident, created)
                Player.players.filter(
                    profile_id=profile_id, realm=realm, region=region
                ).update(identity=ident)
            if game_link:
                Player.players.filter(
                    profile_id=profile_id, realm=realm, region=region
                ).update(game_link=game_link)
