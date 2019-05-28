from parse import *
from fetch import get_all_ladder_responses_for_region
from db import add_players
import asyncio

def update_all_for_region(region):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    future = asyncio.ensure_future(get_all_ladder_responses_for_region(region))
    ladder_list = loop.run_until_complete(future)
    players_to_add = []
    for ladder in ladder_list:
        ladder = parse_ladder(ladder, region)
        for player in ladder:
            players_to_add.append(format_player_for_updating(player))
    try:
        add_players(players_to_add)
    except Exception as e:
        print(e)
    finally:
        loop.close()

def update_all():
    print("updating NA region")
    update_all_for_region(constants.NA_REGION)
    print("updating EU region")
    update_all_for_region(constants.EU_REGION)
    print("updating KR region")
    update_all_for_region(constants.KR_TW_REGION)
    print("database updated")
