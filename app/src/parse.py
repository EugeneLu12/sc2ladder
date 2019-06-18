from typing import List

from django.utils import timezone

from app.models.player import Player


def parse_ladder(response_json, region) -> List[Player]:
    ladder_list = []
    rank = response_json.get('league', {}).get('league_key', {}).get('league_id')
    for i in response_json.get('team'):
        for j in i.get('member'):
            for k in j.get('played_race_count'):
                realm = j.get('legacy_link', {}).get('realm')
                race = k['race']['en_US']
                character_name = j.get('legacy_link', {}).get('name')
                bnet_id = j.get('character_link', {}).get('battle_tag')
                profile_id = j.get('character_link', {}).get('id')
                clan_tag = j.get('clan_link', {}).get('clan_tag')
                try:
                    ladder_list.append(Player.players.create_player(
                        realm=realm,
                        region=region.upper(),
                        rank=int(rank),
                        username=character_name,
                        bnet_id=bnet_id,
                        race=race,
                        mmr=i.get('rating'),
                        wins=i.get('wins'),
                        losses=i.get('losses'),
                        clan=clan_tag,
                        profile_id=profile_id,
                        modified_at=timezone.now()
                    ))
                except:
                    pass

    return ladder_list
