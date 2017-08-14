import build_contentful_data
from flask import Flask, render_template, request, session
from flask_session import Session
import os

import requests

from urlparse import urlparse, urljoin

from os.path import join, dirname
from dotenv import load_dotenv

import pdb

# bookmarklet contents:
# javascript:location.href='http://ec2-34-207-110-254.compute-1.amazonaws.com/add?url='+location.href;

try:
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
except Exception as e:
    print "\nMissing .env file\n"

EVENTBRITE_OAUTH_TOKEN = os.environ.get('EVENTBRITE_OAUTH_TOKEN', None)

EVENTBRITE_API_BASE = 'https://www.eventbriteapi.com/v3/events/'
EVENTBRITE_URL_BASE = 'https://www.eventbrite.com/e/'

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

def get_event_id(url):
    url_components = urlparse(url)
    if not url_components.netloc == 'www.eventbrite.com':
        return None

    # hackily parsing eventbrite urls
    event_name = url_components.path.split('/')[-1]
    event_id = event_name.split('-')[-1]
    return event_id

@app.route("/")
def hello():
    return 'hi hello whats up'

@app.route("/add")
def add():
    url = request.args.get('url', None)
    if url is None:
        return 'You didn\'t pass in a url param!'
    event_id = get_event_id(url)
    if event_id is None:
        return 'This isn\'t an eventbrite page, so we can\'t add it.'
    session['event_id'] = event_id

    return render_template('add.html',
                            categories=build_contentful_data.get_categories(),
                            tags=build_contentful_data.get_tags())

@app.route("/tag", methods=['GET'])
def added():
    event_id = session['event_id']
    api_url = EVENTBRITE_API_BASE + event_id + '?expand=venue'
    response = requests.get(
        api_url,
        headers = {
            "Authorization": "Bearer %s" % EVENTBRITE_OAUTH_TOKEN,
        },
        verify = True,
    )
    title = response.json()['name']['text']
    description = response.json()['description']['text']
    start_time = response.json()['start']['local']
    end_time = response.json()['end']['local']

    external_url = EVENTBRITE_URL_BASE + event_id

    # location data
    lat = float(response.json()['venue']['address']['latitude'])
    lon = float(response.json()['venue']['address']['longitude'])
    name = response.json()['venue']['name']
    room = response.json()['venue']['address']['localized_address_display']
    location_id = build_contentful_data.find_location_id(lat, lon, name, room)

    tags = request.args.getlist('tag')
    event_attributes = build_contentful_data.build_event(title,
                                    start_time=start_time,
                                    end_time=end_time,
                                    description=description,
                                    external_url=external_url,
                                    location_id=location_id,
                                    category=request.args.get('category', None),
                                    tags=tags)

    build_contentful_data.send_to_contentful(event_attributes)
    return 'Added to contentful!'


if __name__ == '__main__':
    app.debug = True
    app.run()
