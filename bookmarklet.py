import build_contentful_data
from flask import Flask, render_template, request, session
from flask_session import Session
import os
import requests
import urllib2

import eventbrite_saver
import localist_saver
import meetup_saver

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

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

URL_HANDLERS = {'www.eventbrite.com' : eventbrite_saver.EventbriteSaver,
                'events.cornell.edu' : localist_saver.LocalistSaver,
                'www.meetup.com' : meetup_saver.MeetupSaver}

@app.route("/")
def hello():
    return render_template('msg.html',
                            msg='Hello!',
                            details='hi hello whats up')

@app.route("/add")
def add():
    url = request.args.get('url', None)
    if url is None:
        return render_template('error.html',
                                details="You didn't pass in a url param!")

    url_details = urlparse(url)
    base_url = url_details.netloc
    if base_url in URL_HANDLERS:
        handler = URL_HANDLERS[base_url]
        try:
            data = handler(url)
            session['data'] = data
        except urllib2.URLError, e:
            return render_template('error.html',
                                    details="Sorry, we can't resolve url",
                                    url=url)
    else:
        return render_template('error.html',
                                details="This isn't a supported page, so we can't add it.")

    # send the template only data that actually exists
    extant_data = {k: v for k,v in vars(data).iteritems() if v is not None}
    print extant_data
    return render_template('add.html',
                            categories=build_contentful_data.get_categories(),
                            tags=build_contentful_data.get_tags(),
                            data = extant_data)

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
        return render_template('msg.html',
                                msg='Success!',
                                details='Your event has been added to the database.')

    return render_template('msg.html',
                            msg='Error',
                            details='There was some sort of problem with fetching your data.')

if __name__ == '__main__':
    app.debug = True
    app.run()
