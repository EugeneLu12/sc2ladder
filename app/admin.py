from django.contrib import admin

from app.models import Player


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    pass
