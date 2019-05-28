from flask import Flask, request, render_template
from shared import constants
from db import search_player_by_bnet_id, search_player_by_name, search_region, get_count_in_region, init_ladder_db
from update_db import update_all
from apscheduler.scheduler import Scheduler
from flask_restful import Api
from sort import *
from player import Player
import atexit

app = Flask(__name__)
api = Api(app)

sched = Scheduler()
sched.start()
sched.add_interval_job(update_all, minutes=10)

api.add_resource(Player, "/api/player")

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/search")
def search_user():
    name = request.args.get('name')
    bnet_id = request.args.get('bnet_id')
    if bnet_id is not None:
        players = search_player_by_bnet_id(str(name) + '#' + str(bnet_id))
    else:
        players = search_player_by_name(name)
    players = sort_results_by_similarity(name, players)
    pages_required = (len(players) > 0) - 1
    return render_template('search.html', players=players, page_number=0, pages_required=pages_required)

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/ladder")
def ladder():
    region = request.args.get('region').upper()
    page_number = int(request.args.get('page'))
    length = get_count_in_region(region)
    players = search_region(region, (page_number - 1)*25, 25)
    players = sort_results_by_mmr(players)
    pages_required = int(length / 25) + 1
    return render_template('search.html', players=players, region=region.lower(),
        page_number=page_number, pages_required=pages_required)

if __name__ == "__main__":
    try:
        init_ladder_db()
    except Exception as e:
        print(e)
    app.run()
