import datetime
import uuid

from django.db import models
from enumfields import EnumIntegerField

from app.models.player import Player, Rank


class PlayerSnapshotManager(models.Manager):
    def create_player_snapshot(self, player: Player) -> 'PlayerSnapshot':
        player_snapshot = self.model(
            player=player,
            rank=player.rank,
            username=player.username,
            mmr=player.mmr,
            wins=player.wins,
            losses=player.losses,
            clan=player.clan,
            bnet_id=player.bnet_id,
        )
        player_snapshot.save()
        return player_snapshot


class PlayerSnapshot(models.Model):
    id: uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    player: Player = models.ForeignKey(Player, on_delete=models.CASCADE)

    rank: Rank = EnumIntegerField(enum=Rank)
    username: str = models.CharField(max_length=30)
    bnet_id: str = models.CharField(max_length=30)
    mmr: int = models.IntegerField()
    wins: int = models.IntegerField()
    losses: int = models.IntegerField()
    clan: str = models.CharField(max_length=10, null=True)

    created_at: datetime = models.DateTimeField(auto_now_add=True)
    modified_at: datetime = models.DateTimeField(auto_now=True)

    player_snapshots = PlayerSnapshotManager()

    def __str__(self):
        return f'{self.id}'
