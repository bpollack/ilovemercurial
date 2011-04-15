from datetime import datetime
import httplib
import json
import sqlite3
import time

from flask import Flask, g, render_template, request
app = Flask(__name__)

import config

## CONFIGURATION

app.config.from_object(config)

## MY USUAL DATABASE HACKERY

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

@app.before_request
def before_request():
    g.db = connect_db()

@app.after_request
def after_request(response):
    g.db.close()
    return response

def q(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

def c(query=None, args=(), one=False):
    if query:
        q(query, args, one)
    g.db.commit()

### Twitter stuff

def update_tweets():
    conn = httplib.HTTPConnection('search.twitter.com')
    conn.request('GET', '/search.json?q=%23ilovemercurial&rpp=100')
    response = conn.getresponse()
    if response.status != 200:
        return False
    data = json.loads(response.read())
    for t in data['results']:
        q('insert or ignore into tweets (id, dt, user, image, text) values (?, ?, ?, ?, ?)',
                   (t['id_str'],
                    time.time(),
                    t['from_user'],
                    t['profile_image_url'],
                    t['text']))
    c()
    return True

## ROUTES

@app.route('/')
def index():
    return render_template('index.html', tweets=q('select * from tweets where approved = 1 order by dt desc limit 30'))

@app.route('/admin')
def admin():
    pass

@app.route('/heartbeat')
def heartbeat():
    ts = q("select value from settings where key = 'last_poll'", one=True)
    ts = float(ts['value']) if ts else None
    if request.args.get('override') or not ts or time.time() - ts > app.config['POLL_INTERVAL']:
        update_tweets()
        ts = time.time()
        c("insert or replace into settings values ('last_poll', ?)", [ts])
    return str(datetime.fromtimestamp(ts))

## AWESOME

if __name__ == '__main__':
    app.run()
