import uplink

BASE_URL = "https://starcraft2.com/en-us/api/sc2/"


class SC2PublicAPI(uplink.Consumer):
    @uplink.get("static/profile/{region}")
    def get_static_profile(self, region: int):
        """Gets static profile"""

    @uplink.get("profile/{region}/{realm}/{profile_id}")
    def get_player_profile(self, region: int, realm: int, profile_id: int):
        """Gets player profile"""

    @uplink.timeout(15)
    @uplink.get("profile/{region}/{realm}/{profile_id}/ladder/summary")
    def get_ladder_summary(self, region: int, realm: int, profile_id: int):
        """Gets a ladder summary"""

    @uplink.timeout(20)
    @uplink.get("profile/{region}/{realm}/{profile_id}/ladder/{ladder_id}")
    def get_ladder(self, region: int, realm: int, profile_id: int, ladder_id: int):
        """Gets ladder"""

    @uplink.get("ladder/season/{region}")
    def get_season(self, region: int):
        """Gets season information"""

    @uplink.get("ladder/grandmaster/{region}")
    def get_grandmaster(self, region: int):
        """Gets grandmaster leaderboard"""
