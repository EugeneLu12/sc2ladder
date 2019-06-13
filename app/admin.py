from django.contrib import admin

from app.models import Player, Identity


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('username', 'bnet_id', 'mmr', 'race')
    readonly_fields = ('created_at', 'modified_at')
    search_fields = ('username', 'bnet_id', 'identity__alias')


@admin.register(Identity)
class IdentityAdmin(admin.ModelAdmin):
    list_display = ('alias', 'first_name', 'last_name')
    readonly_fields = ('created_at', 'modified_at')
    search_fields = ('alias', 'first_name', 'last_name')
