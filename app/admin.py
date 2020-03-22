from django.contrib import admin

from app.models.identity import Identity
from app.models.ladder import Ladder
from app.models.player import Player


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("username", "bnet_id", "clan", "identity", "mmr", "race")
    readonly_fields = ("created_at", "modified_at")
    search_fields = ("username", "bnet_id", "identity__alias")
    ordering = ("-mmr",)


@admin.register(Identity)
class IdentityAdmin(admin.ModelAdmin):
    list_display = ("alias", "first_name", "last_name")
    readonly_fields = ("created_at", "modified_at")
    search_fields = ("alias", "first_name", "last_name")


@admin.register(Ladder)
class LadderAdmin(admin.ModelAdmin):
    list_display = ("rank", "ladder_id", "region", "realm", "profile_id")
    readonly_fields = ("created_at", "modified_at")
    search_fields = ("rank", "ladder_id", "profile_id", "region")
