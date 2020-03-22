from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from app.models.player import Player


class Command(BaseCommand):
    help = "Deletes any player data that is older than 30 days"

    def handle(self, *args, **options):
        now = datetime.now()
        thirty_days_ago = now - timedelta(days=30)
        Player.players.filter(modified_at__lte=thirty_days_ago).delete()
