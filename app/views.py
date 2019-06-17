from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render

from app.models import Player, Rank, Race


class EnumEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, (Rank, Race)):
            return str(obj)
        return super().default(obj)


def api_search(request):
    players = list(
        get_players(request).values('realm', 'region', 'rank', 'username', 'bnet_id', 'race',
                                    'mmr', 'wins', 'losses', 'clan', 'profile_id'))
    return JsonResponse(players, safe=False, encoder=EnumEncoder)


def get_players(request):
    query = request.GET.get('query', '').strip()
    name, bnet_id = query.split('#') if '#' in query else (query, None)
    try:
        limit = min(int(request.GET.get('limit')), settings.MAX_QUERY_LIMIT)
    except (ValueError, TypeError):
        limit = settings.DEFAULT_QUERY_LIMIT

    if bnet_id is not None:
        return Player.players.filter(bnet_id__iexact=f'{name}#{bnet_id}').order_by('-mmr')[:limit]
    else:
        player_filter = Q(bnet_id__istartswith=name) | Q(username__istartswith=name) | Q(identity__alias__iexact=name)
        return Player.players.filter(player_filter).order_by('-mmr')[:limit]


def index(request):
    return render(request, 'index.html')


def search(request):
    players = get_players(request)
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
        'players': players,
        'region_filter': region,
        'regions': ['all', 'US', 'EU', 'KR'],
        'page_number': page_number,
        'pages_required': pages_required,
        'rank_filter': rank,
        'ranks': [name for _, name in reversed(Rank.choices())],
        'sort': sort_by
    })


def about(request):
    return render(request, 'about.html')
