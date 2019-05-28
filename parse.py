import re
import json
from shared import constants

def parse_race(race_json):
    race_dict = json.dumps(race_json['race'])
    race = race_dict[race_dict.index(':'):].strip('\"')
    return re.sub(r'\W+', '', race)

def parse_ladder(response_json, region):
    ladder_list = []
    rank = response_json.get('league', constants.EMPTY_DICT).get('league_key', constants.EMPTY_DICT).get('league_id')
    try:
        for i in response_json.get('team'):
            for j in i.get('member'):
                for k in j.get('played_race_count'):
                    race = parse_race(k)
                    character_name = j.get('legacy_link', constants.EMPTY_DICT).get('name')
                    bnet_id = j.get('character_link', constants.EMPTY_DICT).get('battle_tag')
                    profile_id = j.get('character_link', constants.EMPTY_DICT).get('id')
                    clan_tag = j.get('clan_link', constants.EMPTY_DICT).get('clan_tag')
                    ladder_list.append([region.upper(), rank, character_name, bnet_id, race, i.get('rating'),
                        i.get('wins'), i.get('losses'), clan_tag, str(profile_id),
                        bnet_id + character_name + race])
    except Exception as e:
        print(e)
    return ladder_list

def format_player_for_updating(player):
    return [player[0], player[1], player[2], player[3], player[4], player[5], player[6], player[7],
        player[8], player[9], player[10], player[5], player[6], player[7], player[8]]
        

