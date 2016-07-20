#!/usr/bin/env python

import config

import os
os.chdir(os.path.dirname(config.__file__))

from datetime import datetime
import requests
from flask import Flask, render_template

app = Flask(__name__)
app.config.from_object("config.DevelopmentConfig")

def epoch_to_datetime(epoch):
    #Convert javascript ms epoch to UTC date time
    return datetime.fromtimestamp(epoch / 1000)

def get_events():
    r = requests.get('https://api.meetup.com/nova-makers/events?photo-host=public&page=50&sig_id=9889908&sig=95b5d298133a6b39039e4cf0e63c3c79ed8bb9f1')
    today = []
    upcoming = []
    for event in r.json():
        event['datetime'] = epoch_to_datetime(event['time'])
        event['updated_datetime'] = epoch_to_datetime(event['updated'])
        if datetime.now() > event['datetime']:
            event['status'] = 'started'
        if event['datetime'].date() == datetime.today().date():
            today.append(event)
        else:
            upcoming.append(event)

    return { 'today' : today, 'upcoming' : upcoming }


@app.route('/monitors/1')
def monitor1():
    events = get_events()
    return render_template('index.html', events=events)

@app.route('/monitors/1/updates')
def monitor1update():
    events = get_events()
    return render_template('updates.html', events=events)

@app.template_filter('time')
def format_time(value):
    return value.strftime('%H:%M')

@app.template_filter('dateshort')
def format_date_short(value):
    return value.strftime("%a %b %d<br>%H:%M")

if __name__ == "__main__":
    app.run(host='0.0.0.0')
