from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q, OuterRef, Subquery

from app.models.player import Player
from app.models.player_snapshot import PlayerSnapshot


class Command(BaseCommand):
    help = 'For each player we store a PlayerSnapshot if the data has changed.'

    def handle(self, *args, **options):
        newest_snapshot = PlayerSnapshot.player_snapshots.filter(player=OuterRef('pk')).order_by('-created_at')
        query = Q(wins=Subquery(newest_snapshot.values('wins')[:1])) & Q(
            losses=Subquery(newest_snapshot.values('losses')[:1]))
        players = Player.players.exclude(query)
        print(f'Recording: {players.count()} new PlayerSnapshots.')
        for player in players.iterator(chunk_size=settings.DB_BATCH_SIZE):
            PlayerSnapshot.player_snapshots.create_player_snapshot(player)
        print('Finished')
