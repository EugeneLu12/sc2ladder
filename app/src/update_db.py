import asyncio

from django.conf import settings

from app.models.player import Player, Region
from app.src.parse import parse_ladder, parse_ladder_legacy
from app.src.s2ladderapi import BlizzSession
import os


async def fetch_ladders(region=None):
    loop = asyncio.get_event_loop()
    blz = BlizzSession(os.environ['BLIZZARD_CLIENT_ID'], os.environ['BLIZZARD_CLIENT_SECRET'], loop=loop)
    await blz.get_token()
    if region is None:
        data = await blz.get_all_ladders()
    else:
        data = await blz.get_ladders_by_region(region)
    await blz.close()
    return data


def update_database(region, ladder_list):
    for ladder in ladder_list:
        ladder = parse_ladder(ladder, region)
        Player.players.bulk_create(ladder, batch_size=settings.DB_BATCH_SIZE, ignore_conflicts=True)
        Player.players.bulk_update(
            ladder,
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
    for region in [Region.US.value.lower(), Region.EU.value.lower(), Region.KR.value.lower()]:
        update_gm_for_region_legacy(region)


def update_gm_for_region_legacy(region):
    loop = asyncio.new_event_loop()
    data = loop.run_until_complete(fetch_gm_legacy(region))
    update_database_legacy(region, [data])


async def fetch_gm_legacy(region):
    loop = asyncio.get_event_loop()
    blz = BlizzSession(os.environ['BLIZZARD_CLIENT_ID'], os.environ['BLIZZARD_CLIENT_SECRET'], loop=loop)
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
