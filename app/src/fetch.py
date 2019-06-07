import asyncio
import json

import aiohttp
import requests
from django.conf import settings


def get_token():
    data = {'grant_type': 'client_credentials'}
    r = requests.post('https://us.battle.net/oauth/token', data=data,
                      auth=(settings.BLIZZARD_CLIENT_ID, settings.BLIZZARD_CLIENT_SECRET))
    token = json.loads(r.content).get('access_token')
    return token


def get_all_ladder_ids_for_division(token, season_id, region, division):
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
    }
    r = requests.get(f'https://{region}.api.blizzard.com/data/sc2/league/{season_id}/201/0/{division}?{token}',
                     headers=headers)
    r.raise_for_status()
    ladder_ids = []
    for i in json.loads(r.content).get('tier', {}):
        for j in i.get('division', {}):
            ladder_ids.append(j.get('ladder_id'))
    return ladder_ids


async def fetch_ladder(token, region, ladder_id, session):
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
    }
    url = f'https://{region}.api.blizzard.com/data/sc2/ladder/{ladder_id}?{token}'
    async with session.get(url, headers=headers) as r:
        return await r.json()


async def ladder_scrape(token, region, ladder_ids):
    tasks = []
    async with aiohttp.ClientSession() as session:
        for ladder_id in ladder_ids:
            task = asyncio.ensure_future(fetch_ladder(token, region, ladder_id, session))
            tasks.append(task)
        return await asyncio.gather(*tasks)


def get_cur_season(token, region):
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
    }
    r = requests.get(f'https://us.api.blizzard.com/sc2/ladder/season/{region}?{token}', headers=headers)
    return json.loads(r.content)


async def get_all_ladder_responses_for_region(region):
    ladder_ids = []
    token = get_token()
    season_id = get_cur_season(token, 1).get('seasonId')
    for x in range(7):
        ladder_ids = ladder_ids + get_all_ladder_ids_for_division(token, season_id, region, x)
    return await ladder_scrape(token, region, ladder_ids)
