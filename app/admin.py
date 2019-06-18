from django.contrib import admin

from app.models.identity import Identity
from app.models.player import Player
from app.models.player_snapshot import PlayerSnapshot


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('clan', 'username', 'bnet_id', 'identity', 'mmr', 'race')
    readonly_fields = ('created_at', 'modified_at')
    search_fields = ('username', 'bnet_id', 'identity__alias')


@admin.register(PlayerSnapshot)
class PlayerSnapshotAdmin(admin.ModelAdmin):
    raw_id_fields = ('player',)
    list_display = ('player', 'username', 'bnet_id', 'mmr')
    readonly_fields = ('created_at', 'modified_at')
    search_fields = ('username', 'bnet_id')


@admin.register(Identity)
class IdentityAdmin(admin.ModelAdmin):
    list_display = ('alias', 'first_name', 'last_name')
    readonly_fields = ('created_at', 'modified_at')
    search_fields = ('alias', 'first_name', 'last_name')
