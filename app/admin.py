from django.contrib import admin

from app.models import Player


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('username', 'bnet_id', 'mmr', 'race')
    readonly_fields = ('created_at', 'modified_at')
