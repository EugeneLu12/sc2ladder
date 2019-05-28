from flask_restful import Resource
from flask import request
from db import search_player_by_bnet_id, search_player_by_name
from sort import *
import json

class Player(Resource):

    def get(self):

        name = request.args.get('name')
        bnet_id = request.args.get('bnet_id')
        if bnet_id is not None:
            players = search_player_by_bnet_id(str(name) + '#' + str(bnet_id))
        else:
            players = search_player_by_name(name)
        players = sort_results_by_similarity(name, players)

        keys = ('region', 'rank', 'username', 'bnet_id', 'race', 'mmr', 'wins', 'losses', 'clan', 'id')
        player_dict = [dict(zip(keys, player)) for player in players]
        players_dict = {'players': [player for player in player_dict]}
        if len(players) == 0:
            return 'player not found', 404
        return players_dict
