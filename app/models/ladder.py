import datetime

from django.db import models
from enumfields import EnumIntegerField

from app.models.player import Rank


class Ladder(models.Model):
    ladder_id: str = models.CharField(max_length=12)
    profile_id: str = models.CharField(max_length=12)
    realm: int = models.IntegerField()
    region: int = models.IntegerField()
    rank: Rank = EnumIntegerField(enum=Rank, default=Rank.GOLD.value)
    created_at: datetime = models.DateTimeField(auto_now_add=True)
    modified_at: datetime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.ladder_id
