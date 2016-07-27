#!/usr/bin/env python

import config

import os
os.chdir(os.path.dirname(config.__file__))

import time
from datetime import datetime
import feedparser
import requests
import json
from flask import Flask, render_template, jsonify, url_for, Response

app = Flask(__name__)
app.config.from_object("config.DevelopmentConfig")

def epoch_to_datetime(epoch):
    #Convert javascript ms epoch to UTC date time
    return datetime.fromtimestamp(epoch / 1000)

def get_events():
    r = requests.get('https://api.meetup.com/nova-makers/events?photo-host=public&page=50&sig_id=9889908&sig=95b5d298133a6b39039e4cf0e63c3c79ed8bb9f1')
    today = []
    upcoming = []
    next_refresh = 0
    events = r.json()
    for event in events:
        event['datetime'] = epoch_to_datetime(event['time'])
        event['updated_datetime'] = epoch_to_datetime(event['updated'])
        if datetime.now() > event['datetime']:
            event['status'] = 'started'

        if event['datetime'].date() == datetime.today().date():
            today.append(event)
        else:
            upcoming.append(event)

        if event['datetime'] > datetime.now() and next_refresh == 0:
            next_refresh = (event['time'] / 1000) - time.time()

    return { 'today' : today, 'upcoming' : upcoming, 'next_refresh' : int(next_refresh) * 1000 }

def fetch_headlines():
    headlines = []
    for feed in app.config['FEEDS']:
        parser = feedparser.parse(feed['url'])
        if parser['status'] != 200 or len(parser['entries']) == 0:
            # Error fetching feed, try the next one
            continue
        block = { 'headlines' : [ n['title'] for n in parser['entries'] ][:20] }
        block['icon'] = url_for('static', filename='images/{0}'.format(feed['icon']))
        headlines.append(block)
    return headlines

@app.route('/photos')
def recent_photos():
    photos = get_recent_photos()
    return render_template('photos.html', photos=photos)

def get_recent_photos():
    r = requests.get("https://api.meetup.com/nova-makers/photo_albums?photo-host=public&page=20&sig_id=9889908&sig=5d0d2a89eb3aef511675d9e5552a3d17dcd1674c")
    photos = r.json()
    photo_set = []
    for album in photos:
        for sample in album['photo_sample']:
            date = None
            details = ""
            if 'event' in album.keys():
                album_date = album['event']['time']
                details = "{0} makers went. ".format(album['event']['yes_rsvp_count'])
            else:
                album_date = album['created']
            pic = {
                'src' : sample['photo_link'],
                'title' : album['title'],
                'details' : details,
                'date' : epoch_to_datetime(album_date)
            }
            photo_set.append(pic)
    return photo_set


@app.route('/monitors/1')
def monitor1():
    events = get_events()
    return render_template('index.html', events=events)

@app.route('/monitors/2')
def monitor2():
    events = get_events()
    return render_template('index-2.html', events=events)

@app.route('/monitors/1/updates')
def monitor1update():
    events = get_events()
    return render_template('updates.html', events=events)

@app.route('/headlines')
def get_headlines():
    pass

@app.route('/headlines/json')
def get_headlines_json():
    js = json.dumps(fetch_headlines())
    return Response(js, status=200, mimetype='application/json')


@app.template_filter('time')
def format_time(value):
    return value.strftime('%H:%M')

@app.template_filter('dateshort')
def format_date_short(value):
    return value.strftime("%a<br>%b %d<br>%H:%M")

@app.template_filter('date')
def format_date(value):
    return value.strftime("%Y-%m-%d")

if __name__ == "__main__":
    app.run(host='0.0.0.0')
