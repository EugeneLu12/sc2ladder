from django.test import TestCase

from app.models.player import Player, Race, Rank, Region


class ApiTestCase(TestCase):
    def test_basic(self):
        Player.players.create_player(
            "1",
            Region.US,
            Rank.GRANDMASTER,
            "avilo",
            "avilo#1337",
            Race.TERRAN,
            5666,
            30,
            0,
            "aviNA",
            "123456789",
        ).save()
        response = self.client.get("/api/player?query=avilo")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [
                {
                    "realm": "1",
                    "region": "US",
                    "rank": "Grandmaster",
                    "username": "avilo",
                    "bnet_id": "avilo#1337",
                    "race": "Terran",
                    "mmr": 5666,
                    "wins": 30,
                    "losses": 0,
                    "clan": "aviNA",
                    "profile_id": 123456789,
                    "alias": None,
                }
            ],
        )
