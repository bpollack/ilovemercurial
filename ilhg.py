from datetime import datetime
import httplib
import json
import sqlite3
import time

from flask import Flask, g, render_template, redirect, request, session, url_for
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
        # We don't need the real time stamp; we just need these relatively ordered
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['logged_in'] = (request.form['magic'] == app.config['MAGIC'])
        return redirect(url_for('admin'))
    return '''<form action="" method=post><p>Password: <input type=password name=magic /><input type=submit value=Go /></p></form>'''

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/moderate', methods=['GET', 'POST'])
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        for t in request.form.keys():
            if t.startswith('tweet-'):
                tid = t.split('-')[1]
                status = int(request.form[t])
                q('update tweets set approved = ? where id = ?', [status, tid])
        c()
    return render_template('admin.html', tweets=q('select * from tweets where approved = ? order by dt desc', [int(request.args.get('approved', 0))]))

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
