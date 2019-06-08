from django.db.models import Q
from django.shortcuts import render
from app.models import Player, Rank
from app.serializers import PlayerSerializer
from rest_framework.generics import ListAPIView
from rest_framework.exceptions import APIException

class InvalidQueryException(APIException):
    status_code = 400
    default_detail = "invalid query"

class PlayerList(ListAPIView):
    serializer_class = PlayerSerializer
    def get_queryset(self):
        query = self.request.query_params.get('query')
        try:
            name, bnet_id = query.split('#') if '#' in query else (query, None)
            limit = int(self.request.query_params.get('limit', 25))
            players = get_players(name, bnet_id, limit)
        except:
            raise InvalidQueryException
        return players


def get_players(name=None, bnet_id=None, limit=25):
    limit = min(limit, 200)
    if bnet_id is not None:
        return Player.players.filter(bnet_id__iexact=f'{name}#{bnet_id}').order_by('-mmr')[:limit]
    else:
        bnet_or_name_filter = Q(bnet_id__istartswith=name) | Q(username__istartswith=name)
        return Player.players.filter(bnet_or_name_filter).order_by('-mmr')[:limit]


def index(request):
    return render(request, 'index.html')


def search(request):
    query = request.GET.get('query').strip()
    name, bnet_id = query.split('#') if '#' in query else (query, None)
    limit = int(request.GET.get('limit', 25))
    players = get_players(name, bnet_id, limit)
    pages_required = (len(players) > 0) - 1
    return render(request, 'search.html', {
        'players': players,
        'page_number': 0,
        'pages_required': pages_required
    })


def ladder(request):
    region = request.GET.get('region')
    rank = request.GET.get('rank')
    sort_by = request.GET.get('sort')
    page_number = int(request.GET.get('page'))
    region_query = region if region != 'all' else ''
    rank_query = Rank[rank.upper()].value if rank != 'all' else ''
    
    limit = 25
    start = (page_number - 1) * limit
    end = start + limit
    region_players = Player.players.filter(region__icontains=region_query,
                                        rank__icontains=rank_query)
    length = region_players.count()
    if sort_by == 'mmr':
        players = region_players.order_by('-mmr')[start:end]
    else:
        players = region_players.order_by('-rank', '-mmr')[start:end]
    pages_required = int(length / limit) + 1
    return render(request, 'search.html', {
        "players": players,
        "region_filter": region,
        "regions": ['all', 'US', 'EU', 'KR'],
        "page_number": page_number,
        "pages_required": pages_required,
        "rank_filter": rank,
        "ranks": [str(r) for r in reversed(Rank)],
        "sort": sort_by
    })


def about(request):
    return render(request, 'about.html')
