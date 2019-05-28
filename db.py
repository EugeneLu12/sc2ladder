import psycopg2
import urllib.parse as urlparse
import os

url = urlparse.urlparse(os.environ['DATABASE_URL'])
dbname = url.path[1:]
user = url.username
password = url.password
host = url.hostname
port = url.port

def add_players(players):
    db = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    c = db.cursor()
    c.executemany('''INSERT INTO users(region, rank, username, bnet_id, 
                race, mmr, wins, losses, clan, profile_id, unique_id)
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s)
                ON CONFLICT(unique_id) DO UPDATE
                SET mmr=%s, wins=%s, losses=%s, clan=%s ''', players)
    db.commit()
    db.close()

def init_ladder_db():
    db = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    c = db.cursor()
    c.execute('''
        CREATE TABLE users(region text, rank text, username text, 
                        bnet_id text, race text, mmr int, wins int,
                        losses int, clan text, profile_id text, unique_id text UNIQUE) 
    ''')
    c.execute('''
        CREATE UNIQUE INDEX unique_user_id ON users(unique_id)
    ''')
    db.commit()
    db.close()

def search_player_by_name(username):
    db = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    c = db.cursor()
    c.execute('''SELECT * FROM users WHERE bnet_id ILIKE %s OR username ILIKE %s''', 
        [username + '%', username + '%'])
    players = c.fetchall()
    db.close()
    return players

def search_player_by_bnet_id(bnet_id):
    db = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    c = db.cursor()
    c.execute('''SELECT * FROM users WHERE LOWER(bnet_id)=LOWER(%s)''', (bnet_id,))
    players = c.fetchall()
    db.close()
    return players

def search_player_by_profile_id(region, profile_id):
    db = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    c = db.cursor()
    c.execute('''SELECT * FROM users WHERE region=%s AND profile_id=%s''', (region, profile_id))
    players = c.fetchall()
    db.close()
    return players

def search_region(region, offset, start):
    db = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    c = db.cursor()
    c.execute('''SELECT * FROM users WHERE REGION=%s ORDER BY mmr DESC LIMIT %s OFFSET %s''',
        (region, start, offset))
    players = c.fetchall()
    db.close()
    return players

def get_count_in_region(region):
    db = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    c = db.cursor()
    c.execute('''SELECT count(*) FROM users WHERE REGION=%s''',
        (region,))
    count = c.fetchone()
    db.close()
    return count[0]
