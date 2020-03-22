from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render

from app.models.player import BNET_URI, Player, Race, Rank, Region, age_filter


class EnumEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, (Rank, Race)):
            return str(obj)
        elif isinstance(obj, Region):
            return obj.value
        return super().default(obj)


common_values = [
    "realm",
    "region",
    "rank",
    "username",
    "bnet_id",
    "race",
    "mmr",
    "wins",
    "losses",
    "clan",
    "profile_id",
    "alias",
]


def api_search(request):
    try:
        limit = min(int(request.GET.get("limit")), settings.MAX_QUERY_LIMIT)
    except (ValueError, TypeError):
        limit = settings.DEFAULT_QUERY_LIMIT
    name = request.GET.get("name")
    bnet = request.GET.get("bnet")
    query = request.GET.get("query")
    race = request.GET.get("race")
    region = request.GET.get("region")
    game_link = request.GET.get("gamelink")
    player_filter = Q()
    if name:
        player_filter &= Q(username__iexact=name)
    elif bnet:
        player_filter &= Q(bnet_id__iexact=bnet)
    elif query:
        if query.startswith(BNET_URI):
            game_link = query.replace(BNET_URI, "")
            player_filter = Q(game_link=game_link)
        else:
            q_filter = (
                Q(bnet_id__istartswith=query)
                | Q(username__istartswith=query)
                | Q(identity__alias__iexact=query)
            )
            player_filter &= q_filter
    elif game_link:
        game_link = game_link.replace(BNET_URI, "")
        player_filter &= Q(game_link=game_link)
    if race:
        player_filter &= Q(race__iexact=race)
    if region:
        player_filter &= Q(region__iexact=region)
    players = list(
        Player.actives.filter(player_filter)
        .order_by("-mmr")[:limit]
        .values(*common_values)
    )
    return JsonResponse(players, safe=False, encoder=EnumEncoder)


def api_player(request, region, realm, playerid):
    try:
        limit = min(int(request.GET.get("limit")), settings.MAX_QUERY_LIMIT)
    except (ValueError, TypeError):
        limit = settings.DEFAULT_QUERY_LIMIT
    r_dict = {1: Region.US.value, 2: Region.EU.value, 3: Region.KR.value}
    player_filter = Q(region=r_dict[region], realm=realm, profile_id=playerid)
    players = list(
        Player.actives.filter(player_filter)
        .order_by("-mmr")[:limit]
        .values(*common_values)
    )
    return JsonResponse(players, safe=False, encoder=EnumEncoder)


def api_clans(request, clan_name):
    try:
        limit = min(int(request.GET.get("limit")), settings.MAX_QUERY_LIMIT)
    except (ValueError, TypeError):
        limit = settings.DEFAULT_QUERY_LIMIT
    player_filter = Q(clan__iexact=clan_name)
    player_filter &= Q(clan__iexact=clan_name)
    players = list(
        Player.actives.filter(player_filter)
        .order_by("-mmr")[:limit]
        .values(*common_values)
    )
    return JsonResponse(players, safe=False, encoder=EnumEncoder)


def api_grandmaster(request, region):
    player_filter = Q(rank=Rank.GRANDMASTER, region=region.upper())
    # filter out gm dropouts who haven't yet been updated
    players = list(
        Player.actives.filter(player_filter)
        .filter(age_filter(days=0.1))
        .order_by("-mmr")
        .values(*common_values)
    )
    # if no players were updated within 2.4 hours then we had an updating problem, so just return what we currently have
    if len(players) < 1:
        players = list(
            Player.actives.filter(player_filter).order_by("-mmr").values(*common_values)
        )
    return JsonResponse(players, safe=False, encoder=EnumEncoder)


def get_players(request):
    try:
        limit = min(int(request.GET.get("limit")), settings.MAX_QUERY_LIMIT)
    except (ValueError, TypeError):
        limit = settings.DEFAULT_QUERY_LIMIT

    query: str = request.GET.get("query", "").strip()
    if "#" in query:
        # Probably trying to search by battlenet e.g. avilo#1337.
        player_filter = Q(bnet_id__iexact=query)
    elif query.startswith(BNET_URI):
        game_link = query.replace(BNET_URI, "")
        player_filter = Q(game_link=game_link)
    elif query.startswith("[") and query.endswith("]"):
        # Probably trying to search by clan e.g. [aviNA]. We don't limit this since it's automatically
        # limited by Sc2.
        clan = query[1:-1]
        player_filter = Q(clan__iexact=clan)
    else:
        # Probably just searching by name e.g. avilo.
        player_filter = (
            Q(bnet_id__istartswith=query)
            | Q(username__istartswith=query)
            | Q(identity__alias__iexact=query)
        )
    return Player.actives.filter(player_filter).order_by("-mmr")[:limit]


def index(request):
    return render(request, "index.html")


def search(request):
    players = get_players(request)
    pages_required = (len(players) > 0) - 1
    return render(
        request,
        "search.html",
        {"players": players, "page_number": 0, "pages_required": pages_required},
    )


def ladder(request):
    region = request.GET.get("region", "us")
    rank = request.GET.get("rank", "all")
    sort_by = request.GET.get("sort", "mmr")
    page_number = int(request.GET.get("page", 1))
    region_query = region if region != "all" else ""
    rank_query = Rank[rank.upper()].value if rank != "all" else ""

    limit = 25
    start = (page_number - 1) * limit
    end = start + limit
    region_players = Player.actives.filter(
        region__icontains=region_query, rank__icontains=rank_query
    )
    length = region_players.count()
    if sort_by == "mmr":
        players = region_players.order_by("-mmr")[start:end]
    else:
        players = region_players.order_by("-rank", "-mmr")[start:end]
    pages_required = int(length / limit) + 1
    return render(
        request,
        "search.html",
        {
            "players": players,
            "region_filter": region,
            "regions": ["all", "US", "EU", "KR"],
            "page_number": page_number,
            "pages_required": pages_required,
            "rank_filter": rank,
            "ranks": [name for _, name in reversed(Rank.choices())],
            "sort": sort_by,
        },
    )


def about(request):
    return render(request, "about.html")
