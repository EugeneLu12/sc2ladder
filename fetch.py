import requests
import aiohttp
import asyncio
import json
from shared import constants, credentials

def get_token():
    data = { 'grant_type': 'client_credentials' }
    try:
        r = requests.post('https://us.battle.net/oauth/token', data=data, auth=(credentials.client_id, credentials.client_secret))
    except requests.exceptions.RequestException as e:
        print(e)
    token = json.loads(r.content).get('access_token')
    return token

def get_all_ladder_ids_for_division(token, season_id, region, division):
    headers = {
        'Authorization': 'Bearer ' + token,
        'Accept': 'application/json',
    }
    try:
        r = requests.get('https://' + region + '.api.blizzard.com/data/sc2/league/' +
            str(season_id) + '/201/0/' + str(division) + '?' + token, headers=headers)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(e)
    ladder_ids = []
    for i in json.loads(r.content).get('tier', constants.EMPTY_DICT):
        for j in i.get('division', constants.EMPTY_DICT):
            ladder_ids.append(j.get('ladder_id'))
    return ladder_ids

async def fetch_ladder(token, region, ladder_id, session):
    headers = {
        'Authorization': 'Bearer ' + token,
        'Accept': 'application/json',
    }
    url = 'https://' + region + '.api.blizzard.com/data/sc2/ladder/' + str(ladder_id) + '?' + token
    async with session.get(url, headers=headers) as r:
            print('fetching ladder id: ' + str(ladder_id))
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
        'Authorization': 'Bearer ' + token,
        'Accept': 'application/json',
    }
    try:
        r = requests.get('https://us.api.blizzard.com/sc2/ladder/season/' + str(region) + '?' + token, headers=headers)
    except requests.exceptions.RequestException as e:
        print(e)
    return json.loads(r.content)

async def get_all_ladder_responses_for_region(region):
    ladder_ids = []
    token = get_token()
    season_id = get_cur_season(token, 1).get('seasonId')
    for x in range(7):
       ladder_ids = ladder_ids + get_all_ladder_ids_for_division(token, season_id, region, x)
    return await ladder_scrape(token, region, ladder_ids)
