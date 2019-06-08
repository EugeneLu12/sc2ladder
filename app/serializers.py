from rest_framework import serializers
from app.models import Player, Rank, Race


class EnumField(serializers.ChoiceField):
    def __init__(self, enum, **kwargs):
        self._enum = enum
        kwargs['choices'] = [(e.name, e.name) for e in enum]
        super(EnumField, self).__init__(**kwargs)

    def to_representation(self, obj):
        return obj.name

    def to_internal_value(self, data):
        try:
            return self._enum[data]
        except KeyError:
            self.fail('invalid choice', input=data)


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = '__all__'
    rank = EnumField(enum=Rank)
    race = EnumField(enum=Race)