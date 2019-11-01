from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render

from app.models.player import Player, Rank, Race, Region


class EnumEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, (Rank, Race)):
            return str(obj)
        elif isinstance(obj, Region):
            return obj.value
        return super().default(obj)


def api_search(request):
    players = list(
        get_players(request).values('realm', 'region', 'rank', 'username', 'bnet_id', 'race',
                                    'mmr', 'wins', 'losses', 'clan', 'profile_id'))
    return JsonResponse(players, safe=False, encoder=EnumEncoder)


def get_players(request):
    try:
        limit = min(int(request.GET.get('limit')), settings.MAX_QUERY_LIMIT)
    except (ValueError, TypeError):
        limit = settings.DEFAULT_QUERY_LIMIT

    query: str = request.GET.get('query', '').strip()
    if '#' in query:
        # Probably trying to search by battlenet e.g. avilo#1337.
        name, bnet_id = query.split('#')
        return Player.players.filter(bnet_id__iexact=f'{name}#{bnet_id}').order_by('-mmr')[:limit]
    elif query.startswith('[') and query.endswith(']'):
        # Probably trying to search by clan e.g. [aviNA]. We don't limit this since it's automatically
        # limited by Sc2.
        clan = query[1:-1]
        return Player.players.filter(clan__iexact=clan).order_by('-mmr')
    else:
        # Probably just searching by name e.g. avilo.
        player_filter = Q(bnet_id__istartswith=query) | \
                        Q(username__istartswith=query) | \
                        Q(identity__alias__iexact=query)
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
    region = request.GET.get('region', 'us')
    rank = request.GET.get('rank', 'all')
    sort_by = request.GET.get('sort', 'mmr')
    page_number = int(request.GET.get('page', 1))
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
