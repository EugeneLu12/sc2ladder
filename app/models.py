import datetime

from django.db import models
from enumfields import Enum, EnumIntegerField, EnumField


class Rank(Enum):
    BRONZE = 0
    SILVER = 1
    GOLD = 2
    PLATINUM = 3
    DIAMOND = 4
    MASTER = 5
    GRANDMASTER = 6


class Race(Enum):
    ZERG = 'Zerg'
    TERRAN = 'Terran'
    PROTOSS = 'Protoss'
    RANDOM = 'Random'


class Identity(models.Model):
    alias = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    created_at: datetime = models.DateTimeField(auto_now_add=True)
    modified_at: datetime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.alias


class PlayerManager(models.Manager):
    def create_player(self, realm: str, region: str, rank: Rank, username: str, bnet_id: str, race: str, mmr: int,
                      wins: int, losses: int, clan: str, profile_id: str, **extra_fields) -> 'Player':
        """
        Note that this doesn't actually save the player in the DB. It simply returns a Player object.
        """
        unique_id = f'{realm}/{region}/{profile_id}-{race}'
        player = self.model(
            id=unique_id,
            realm=realm,
            region=region,
            rank=rank,
            username=username,
            bnet_id=bnet_id,
            race=race,
            mmr=mmr,
            wins=wins,
            losses=losses,
            clan=clan,
            profile_id=profile_id,
            **extra_fields
        )
        return player


class Player(models.Model):
    id: str = models.CharField(max_length=50, primary_key=True, editable=False)
    realm: str = models.CharField(max_length=10)
    region: str = models.CharField(max_length=10)
    rank: Rank = EnumIntegerField(enum=Rank)
    username: str = models.CharField(max_length=30)
    bnet_id: str = models.CharField(max_length=30)
    race: Race = EnumField(Race, max_length=7)
    mmr: int = models.IntegerField()
    wins: int = models.IntegerField()
    losses: int = models.IntegerField()
    clan: str = models.CharField(max_length=10, null=True, blank=True)
    profile_id: int = models.IntegerField()
    identity = models.ForeignKey(Identity, null=True, blank=True, on_delete=models.SET_NULL)
    created_at: datetime = models.DateTimeField(auto_now_add=True)
    modified_at: datetime = models.DateTimeField(auto_now=True)

    players = PlayerManager()

    def __str__(self):
        return self.id
