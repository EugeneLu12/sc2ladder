from typing import List
from django.utils import timezone
from app.models.player import Player, Rank


def parse_ladder(response_json, region) -> List[Player]:
    ladder_list = []
    rank = int(response_json.get('league', {}).get('league_key', {}).get('league_id', 0))
    for team in response_json.get('team', []):
        for member in team.get('member', []):
            for k in member.get('played_race_count', []):
                try:
                    realm = member['legacy_link']['realm']
                    race = k['race']['en_US'].capitalize()
                    character_name = member['legacy_link']['name']
                    bnet_id = member['character_link']['battle_tag']
                    profile_id = member['character_link']['id']
                    clan_tag = member.get('clan_link', {}).get('clan_tag')
                    mmr = team['rating']
                    wins = team['wins']
                    losses = team['losses']
                    ladder_list.append(Player.players.create_player(
                        realm=realm,
                        region=region.upper(),
                        rank=rank,
                        username=character_name,
                        bnet_id=bnet_id,
                        race=race,
                        mmr=mmr,
                        wins=wins,
                        losses=losses,
                        clan=clan_tag,
                        profile_id=profile_id,
                        modified_at=timezone.now()
                    ))
                except:
                    pass
    return ladder_list


def parse_ladder_legacy(response_json, region) -> List[Player]:
    ladder_list = []
    rank = Rank.GRANDMASTER.value
    for team in response_json.get('ladderTeams', []):
        for member in team['teamMembers']:
            try:
                realm = member['realm']
                race = member['favoriteRace']
                character_name = member['displayName'] + '#0000'  # must include dummy discriminator for new players
                bnet_id = None
                profile_id = int(member['id'])
                clan_tag = member.get('clanTag')
                mmr = team['mmr']
                wins = team['wins']
                losses = team['losses']
                ladder_list.append(Player.players.create_player(
                    realm=realm,
                    region=region.upper(),
                    rank=rank,
                    username=character_name,
                    bnet_id=bnet_id,
                    race=race.capitalize(),
                    mmr=mmr,
                    wins=wins,
                    losses=losses,
                    clan=clan_tag,
                    profile_id=profile_id,
                    modified_at=timezone.now()
                ))
            except:
                pass
    return ladder_list
