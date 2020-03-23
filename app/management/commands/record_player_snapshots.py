from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from app.models.player import Player


class Command(BaseCommand):
    help = "For each player we store a {<date>: mmr} in their mmr_history column if their mmr has changed."

    def handle(self, *args, **options):
        print(f"Started updating mmr_history")
        for player in Player.actives.iterator(chunk_size=settings.DB_BATCH_SIZE):
            now = int(timezone.now().timestamp())
            mmr_history = player.mmr_history
            most_recent_mmr = mmr_history.get(
                max(mmr_history or [0], key=int), None  # Max throws for {}
            )
            if player.mmr != most_recent_mmr:
                player.mmr_history = {**player.mmr_history, now: player.mmr}
            player.save()

        print("Finished updating mmr_history")
