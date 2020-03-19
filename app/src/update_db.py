import asyncio

import uplink
from django.conf import settings

from app.models.player import Player, Region, Rank
from app.models.ladder import Ladder
from app.src.laddercrawler import LadderCrawler
from app.src.sc2publicapi import SC2PublicAPI, BASE_URL
from app.src.parse import parse_ladder, parse_ladder_legacy, parse_public_players
from app.src.s2ladderapi import BlizzSession
from constance import config
from django.db.models import Q


async def fetch_ladders(region=None):
    loop = asyncio.get_event_loop()
    blz = BlizzSession(settings.BLIZZARD_CLIENT_ID, settings.BLIZZARD_CLIENT_SECRET, loop=loop)
    await blz.get_token()
    if region is None:
        data = await blz.get_all_ladders()
    else:
        data = await blz.get_ladders_by_region(region)
    await blz.close()
    return data


def update_database(region, ladder_list):
    step_size = config.STEP_SIZE
    for i in range(0, len(ladder_list), step_size):
        update_list = []
        for ladder in ladder_list[i:i+step_size]:
            update_list += parse_ladder(ladder, region)
        Player.players.bulk_create(update_list, batch_size=settings.DB_BATCH_SIZE, ignore_conflicts=True)
        Player.players.bulk_update(
            update_list,
            ['bnet_id', 'username', 'mmr', 'wins', 'losses', 'clan', 'rank', 'modified_at'],
            batch_size=settings.DB_BATCH_SIZE
        )


def update_all_for_region(region):
    loop = asyncio.new_event_loop()
    data = loop.run_until_complete(fetch_ladders(region))
    loop.close()
    update_database(region, data)


def update_all():
    loop = asyncio.new_event_loop()
    data = loop.run_until_complete(fetch_ladders())
    loop.close()
    for region in data:
        update_database(region['region'], region['data'])


def update_all_gm_legacy():
    for _, region in Region.choices():
        update_gm_for_region_legacy(region.lower())


def update_gm_for_region_legacy(region):
    loop = asyncio.new_event_loop()
    data = loop.run_until_complete(fetch_gm_legacy(region))
    update_database_legacy(region, [data])


async def fetch_gm_legacy(region):
    loop = asyncio.get_event_loop()
    blz = BlizzSession(settings.BLIZZARD_CLIENT_ID, settings.BLIZZARD_CLIENT_SECRET, loop=loop)
    await blz.get_token()
    data = await blz.get_grandmaster_leaderboard(region)
    await blz.close()
    return data


def update_database_legacy(region, ladder_list):
    for ladder in ladder_list:
        ladder = parse_ladder_legacy(ladder, region)
        Player.players.bulk_create(ladder, batch_size=settings.DB_BATCH_SIZE, ignore_conflicts=True)
        Player.players.bulk_update(
            ladder,
            ['mmr', 'wins', 'losses', 'clan', 'rank', 'modified_at'],
            batch_size=settings.DB_BATCH_SIZE
        )


def fetch_public_ladders(region, league=None):
    league_dict = {
        "grandmaster": Rank.GRANDMASTER.value,
        "master": Rank.MASTER.value,
        "diamond": Rank.DIAMOND.value,
        "platinum": Rank.PLATINUM.value,
        "gold": Rank.GOLD.value,
        "silver": Rank.SILVER.value,
        "bronze": Rank.BRONZE.value,
    }

    ladder_filter = Q(rank=league_dict[league], region=region)
    ladder = Ladder.objects.filter(ladder_filter).order_by('?').first()
    realm, profile_id, ladder_id = None, None, None
    if ladder:
        realm, profile_id, ladder_id = ladder.realm, ladder.profile_id, ladder.ladder_id

    api_as = SC2PublicAPI(BASE_URL, client=uplink.AiohttpClient())
    crawler = LadderCrawler(api_as, max_requests=512)
    loop = asyncio.get_event_loop()

    # TODO: Can filter out recently updated ladders or players
    #  ladder_ids = [ladder.ladder_id for ladder in Ladder.objects.filter(ladder_filter)]
    #  player_filter = Q(rank=league_dict[league], region=Region.EU.value)
    #  profile_ids = [str(player.profile_id) for player in Player.players.filter(player_filter)]
    #  crawler.ladder_ids = ladder_ids
    #  crawler.profile_ids = profile_ids

    ladder_infos = loop.run_until_complete(crawler.get_adjacent_ladders(
                                                region=region,
                                                league=league,
                                                realm=realm,
                                                profile_id=profile_id,
                                                ladder_id=ladder_id
                                                                        )
                                            )
    return ladder_infos


def update_database_public_ladders(ladder_infos):
    for ladder in ladder_infos:
        if ladder is None:
            continue
        league_dict = {"grandmaster": Rank.GRANDMASTER.value, "master": Rank.MASTER.value,
                       "diamond": Rank.DIAMOND.value, "platinum": Rank.PLATINUM.value, "gold": Rank.GOLD.value,
                       "silver": Rank.SILVER.value, "bronze": Rank.BRONZE.value}
        Ladder.objects.update_or_create(ladder_id=ladder.ladder_id,
                                        region=ladder.p.region,
                                        defaults={'realm': ladder.p.realm,
                                                  'profile_id': ladder.p.profile_id,
                                                  'rank': league_dict[ladder.league]
                                                  }
                                        )


def update_public_ladders(region, league=None):
    region_dict = {'us': 1, 'eu': 2, 'kr': 3}
    region = region_dict.get(region)
    if region is None:
        for r in range(1, 4):
            ladders = fetch_public_ladders(region=r, league=league)
            update_database_public_ladders(ladders)
    else:
        ladders = fetch_public_ladders(region=region, league=league)
        update_database_public_ladders(ladders)


def fetch_public_players(region, league=None):
    api_as = SC2PublicAPI(BASE_URL, client=uplink.AiohttpClient())
    crawler = LadderCrawler(api_as, max_requests=12)
    loop = asyncio.get_event_loop()
    bundle_list = list()
    league_dict = {"grandmaster": Rank.GRANDMASTER.value, "master": Rank.MASTER.value,
                   "diamond": Rank.DIAMOND.value, "platinum": Rank.PLATINUM.value, "gold": Rank.GOLD.value,
                   "silver": Rank.SILVER.value, "bronze": Rank.BRONZE.value}
    if league is not None:
        player_filter = Q(rank=league_dict[league], region=region)
    else:
        player_filter = Q(region=region)

    for ladder in Ladder.objects.filter(player_filter):
        bundle_list.append((ladder.region, ladder.realm, ladder.profile_id, ladder.ladder_id))

    players = loop.run_until_complete(crawler.get_player_dump(bundle_list))
    return players


def update_database_public_players(players):
    ladder = parse_public_players(players)
    Player.players.bulk_create(ladder, batch_size=settings.DB_BATCH_SIZE, ignore_conflicts=True)
    Player.players.bulk_update(
        ladder,
        ['mmr', 'wins', 'losses', 'clan', 'rank', 'modified_at', 'username'],
        batch_size=settings.DB_BATCH_SIZE
    )


def update_public_players(region, league=None):
    region_dict = {'us': 1, 'eu': 2, 'kr': 3}
    region = region_dict.get(region)
    if region is None:
        for r in range(1, 4):
            players = fetch_public_players(region=r, league=league)
            update_database_public_players(players)
    else:
        players = fetch_public_players(region=region, league=league)
        update_database_public_players(players)
