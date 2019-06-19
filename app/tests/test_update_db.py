import json
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from app.models.player import Player, Rank, Race, Region


async def return_this(this):
    return this


class UpdateDbTestCase(TestCase):
    @patch('app.src.fetch.get_all_ladder_responses_for_region')
    def test_one_player(self, mock_get):
        with open('app/tests/one_player.json') as f:
            mock_get.return_value = return_this(json.load(f))

        call_command('update_db', region='us')
        self.assertEqual(Player.players.all().count(), 1)
        avilo: Player = Player.players.first()
        self.assertEqual(avilo.bnet_id, 'avilo#1337')
        self.assertEqual(avilo.rank, Rank.GRANDMASTER)
        self.assertEqual(avilo.mmr, 5678)
        self.assertEqual(avilo.wins, 32)
        self.assertEqual(avilo.losses, 18)
        self.assertEqual(avilo.race, Race.TERRAN)
        self.assertEqual(avilo.clan, 'aivNA')
        self.assertEqual(avilo.profile_id, 12345679)
        self.assertEqual(avilo.username, 'avilo')
        self.assertEqual(avilo.realm, '1')
        self.assertEqual(avilo.region, Region.US)
