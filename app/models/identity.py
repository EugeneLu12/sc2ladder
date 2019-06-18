import datetime

from django.db import models


class Identity(models.Model):
    alias = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    twitch = models.CharField(max_length=30, null=True, blank=True)

    created_at: datetime = models.DateTimeField(auto_now_add=True)
    modified_at: datetime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.alias
