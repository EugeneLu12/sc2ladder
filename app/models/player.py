import datetime
from django.utils import timezone
from django.db import models
from enumfields import Enum, EnumIntegerField, EnumField

from app.models.identity import Identity
from constance import config


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


class Region(Enum):
    US = 'US'
    EU = 'EU'
    KR = 'KR'


def age_filter(days=config.AGE_LIMIT):
    now = timezone.now()
    days_ago = now - timezone.timedelta(days=days)
    return models.Q(modified_at__gte=days_ago)


class ActivePlayerManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(age_filter())


class PlayerManager(models.Manager):
    def create_player(self, realm: str, region: Region, rank: Rank, username: str, bnet_id: str, race: Race, mmr: int,
                      wins: int, losses: int, clan: str, profile_id: str, **extra_fields) -> 'Player':
        """
        Note that this doesn't actually save the player in the DB. It simply returns a Player object.
        """
        if int(mmr) > 2147483646:
            mmr = 2147483646
        elif int(mmr) < -2147483647:
            mmr = -2147483647
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
    region: str = EnumField(Region, max_length=2)
    rank: Rank = EnumIntegerField(enum=Rank)
    username: str = models.CharField(max_length=30)
    bnet_id: str = models.CharField(max_length=30, null=True, blank=True)

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
    actives = ActivePlayerManager()

    def __str__(self):
        return self.id
