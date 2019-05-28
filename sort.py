from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def sort_results_by_similarity(search_str, player_list):
    search_str = search_str.lower()
    new_player_list = []
    sorted_player_list = []
    for player in player_list:
        bnet_id = player[3][:player[3].index('#')].lower()
        username = player[2][:player[2].index('#')].lower()
        similarity = max(similar(search_str, bnet_id),
            similar(search_str, username))
        sorted_player_list.append([player, similarity])
    sorted_player_list = sorted(sorted_player_list, key=lambda x: (-x[1],-x[0][5]))
    for player in sorted_player_list:
        new_player_list.append(player[0])
    return new_player_list

def sort_results_by_mmr(player_list):
    sorted_player_list = sorted(player_list, key=lambda x: x[5], reverse=True)
    return sorted_player_list