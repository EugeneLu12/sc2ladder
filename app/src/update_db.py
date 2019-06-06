import asyncio
import logging

from app.models import Player
from app.src.fetch import get_all_ladder_responses_for_region
from app.src.parse import parse_ladder

logger = logging.getLogger(__name__)

NA_REGION = 'us'
EU_REGION = 'eu'
KR_TW_REGION = 'kr'
CN_REGION = 'cn'


def update_all_for_region(region):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    future = asyncio.ensure_future(get_all_ladder_responses_for_region(region))
    ladder_list = loop.run_until_complete(future)
    players_to_add = []
    for ladder in ladder_list:
        ladder = parse_ladder(ladder, region)
        players_to_add += ladder
    Player.players.bulk_create(players_to_add, batch_size=450, ignore_conflicts=True)
    Player.players.bulk_update(players_to_add, ['mmr', 'wins', 'losses', 'clan', 'rank'],  batch_size=450)
    loop.close()


def update_all():
    logging.info("updating NA region")
    update_all_for_region(NA_REGION)
    # logging.info("updating EU region")
    # update_all_for_region(EU_REGION)
    # logging.info("updating KR region")
    # update_all_for_region(KR_TW_REGION)
    logging.info("database updated")
