from rest_framework import serializers
from app.models import Player

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ('region', 'realm', 'username', 'bnet_id', 'mmr', 'wins', 'losses', 'clan')