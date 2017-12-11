import build_contentful_data
from flask import Flask, render_template, request, session
from flask_session import Session
import os
import requests

import eventbrite_saver
import localist_saver

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

URL_HANDLERS = {'www.eventbrite.com' : eventbrite_saver.EventbriteSaver,
                'events.cornell.edu' : localist_saver.LocalistSaver}

@app.route("/")
def hello():
    return 'hi hello whats up'

@app.route("/add")
def add():
    url = request.args.get('url', None)
    if url is None:
        return 'You didn\'t pass in a url param!'

    url_details = urlparse(url)
    base_url = url_details.netloc
    if base_url in URL_HANDLERS:
        handler = URL_HANDLERS[base_url]
        data = handler(url)
        session['data'] = data
    else:
        return 'This isn\'t a supported page, so we can\'t add it.'

    return render_template('add.html',
                            categories=build_contentful_data.get_categories(),
                            tags=build_contentful_data.get_tags())

@app.route("/tag", methods=['GET'])
def added():
    tags = request.args.getlist('tag')
    category=request.args.get('category', None)
    data = session.get('data')
    if data:
        event_attributes = build_contentful_data.build_event(data.title,
                                        start_time=data.start_time,
                                        end_time=data.end_time,
                                        description=data.description,
                                        external_url=data.url,
                                        location_id=data.location_id,
                                        category=category,
                                        tags=tags)

        build_contentful_data.send_to_contentful(event_attributes)
        return 'Added to contentful!'

    return 'There was some sort of problem with fetching your data.'

if __name__ == '__main__':
    app.debug = True
    app.run()
