import asyncio
import json
import random
from typing import List


class PlayerInfo:
    def __init__(
        self,
        region: int,
        realm: int,
        profile_id: int,
        username: str = None,
        clan_tag: str = None,
        race: str = None,
        wins: int = None,
        losses: int = None,
        mmr: int = None,
        league: str = None,
    ):
        self.region = region
        self.realm = realm
        self.profile_id = profile_id
        self.username = username
        self.clan_tag = clan_tag
        self.race = race
        self.wins = wins
        self.losses = losses
        self.mmr = mmr
        self.league = league

    def __str__(self):
        return f"{self.username} {self.profile_id} {self.race} {self.region}"

    def __repr__(self):
        return (
            f"<PlayerInfo {self.username} {self.profile_id} {self.race} {self.region}>"
        )


class LadderInfo:
    def __init__(self, player: PlayerInfo, ladder_id: int, league: str = None):
        self.player = player
        self.p = self.player
        self.league = league
        self.ladder_id = ladder_id

    def __str__(self):
        return (
            f"<LadderInfo https://starcraft2.com/en-us/api/sc2/"
            f"profile/{self.p.region}/{self.p.realm}/{self.p.profile_id}/ladder/{self.ladder_id} {self.league}>"
        )

    def __repr__(self):
        return (
            f"<LadderInfo https://starcraft2.com/en-us/api/sc2/"
            f"profile/{self.p.region}/{self.p.realm}/{self.p.profile_id}/ladder/{self.ladder_id} {self.league}>"
        )


class LadderCrawler:
    def __init__(self, api, max_requests=10 ** 4):
        self.api = api
        self.curr_requests = 0
        self.max_requests = max_requests
        self.ladder_ids = list()
        self.profile_ids = list()

    async def _get_ladder_data(
        self,
        region: int,
        realm: int = None,
        profile_id: int = None,
        ladder_id: int = None,
    ) -> dict:
        while self.curr_requests >= self.max_requests:
            await asyncio.sleep(5)
        self.curr_requests += 1
        try:
            if profile_id is None:
                resp = await self.api.get_grandmaster(region)
            else:
                resp = await self.api.get_ladder(
                    region=region,
                    realm=realm,
                    profile_id=profile_id,
                    ladder_id=ladder_id,
                )
            result = json.loads(await resp.text())
        except:
            result = {"ladderTeams": []}
        self.curr_requests -= 1
        return result

    async def _get_summary(self, region, realm, pid) -> dict:
        # check cache
        while self.curr_requests >= self.max_requests:
            await asyncio.sleep(5)
        self.curr_requests += 1
        try:
            resp = await self.api.get_ladder_summary(region, realm, pid)
            if resp.status == 200:
                summary = json.loads(await resp.text())
                result = summary
            else:
                result = {"allLadderMemberships": []}
        except asyncio.TimeoutError:
            result = {"allLadderMemberships": []}
        self.curr_requests -= 1
        return result

    async def get_ladder_data(self, ladder_about: LadderInfo) -> List[PlayerInfo]:
        raw_ladder = await self._get_ladder_data(
            ladder_about.p.region,
            ladder_about.p.realm,
            ladder_about.p.profile_id,
            ladder_about.ladder_id,
        )
        p_list = list()
        for team in raw_ladder.get("ladderTeams", []):
            member = team["teamMembers"][0]
            player = PlayerInfo(
                region=member.get("region"),
                realm=member.get("realm"),
                profile_id=member.get("id"),
                username=member.get("displayName"),
                clan_tag=member.get("clanTag"),
                race=member.get("favoriteRace"),
                wins=team.get("wins"),
                losses=team.get("losses"),
                mmr=team.get("mmr"),
                league=raw_ladder.get("league"),
            )
            p_list.append(player)
        return p_list

    async def get_grandmaster_data(self, region: int = None) -> List[PlayerInfo]:
        raw_ladder = await self._get_ladder_data(region)
        p_list = list()
        for team in raw_ladder.get("ladderTeams", []):
            member = team["teamMembers"][0]
            player = PlayerInfo(
                region=member.get("region"),
                realm=member.get("realm"),
                profile_id=member.get("id"),
                username=member.get("displayName"),
                clan_tag=member.get("clanTag"),
                race=member.get("favoriteRace"),
                wins=team.get("wins"),
                losses=team.get("losses"),
                mmr=team.get("mmr"),
                league=raw_ladder.get("league"),
            )
            p_list.append(player)
        return p_list

    async def get_ladder_infos(self, player: PlayerInfo) -> List[LadderInfo]:
        raw_summary = await self._get_summary(
            player.region, player.realm, player.profile_id
        )
        la_list = list()
        for ladder in raw_summary.get("allLadderMemberships"):
            league = ladder.get("localizedGameMode", "1v1 Master")
            ladder_about = LadderInfo(
                player=player,
                league=league.split(" ")[-1].lower(),
                ladder_id=ladder.get("ladderId"),
            )
            if league.startswith("1v1"):
                la_list.append(ladder_about)
        return la_list

    async def get_player_dump(self, bundle_list) -> List[PlayerInfo]:
        tasklist = []
        for bundle in bundle_list:
            player = PlayerInfo(region=bundle[0], realm=bundle[1], profile_id=bundle[2])
            ladder = LadderInfo(player=player, ladder_id=bundle[3])
            tasklist.append(self.get_ladder_data(ladder))
        res = await asyncio.gather(*tasklist)
        return [item for sublist in res for item in sublist]

    async def get_sub_ladders(
        self, root_ladder: LadderInfo = None, league: str = None, region: int = None
    ) -> List[LadderInfo]:
        if root_ladder is not None:
            players = await self.get_ladder_data(root_ladder)
        else:
            players = await self.get_grandmaster_data(region)

        players = [p for p in players if p is not None]
        players = [p for p in players if p.profile_id not in self.profile_ids]
        for p in players:
            self.profile_ids.append(p.profile_id)
        random.shuffle(players)

        ladder_infos = await asyncio.gather(
            *[self.get_ladder_infos(p) for p in players]
        )
        ladder_infos = [item for sublist in ladder_infos for item in sublist]  # flatten

        # we save vladder_infos separately so we can only dive deeper into divions in the same league
        # but will still save the references we found to other ladder divions to return
        if league is not None:
            vladder_infos = [
                l_info for l_info in ladder_infos if l_info.league == league.lower()
            ]
        else:
            vladder_infos = ladder_infos

        for l_about in ladder_infos[:]:
            if l_about.ladder_id in self.ladder_ids:
                ladder_infos.remove(l_about)
            else:
                self.ladder_ids.append(l_about.ladder_id)

        res = await asyncio.gather(
            *[self.get_sub_ladders(l_info, league) for l_info in vladder_infos]
        )
        return ladder_infos + [item for sublist in res for item in sublist]

    async def get_adjacent_ladders(
        self, region=None, league=None, realm=None, profile_id=None, ladder_id=None
    ):
        ladder_info = None
        if profile_id is not None:
            player_info = PlayerInfo(region=region, realm=realm, profile_id=profile_id)
            ladder_info = LadderInfo(player=player_info, ladder_id=ladder_id)
        return await self.get_sub_ladders(
            root_ladder=ladder_info, league=league, region=region
        )
