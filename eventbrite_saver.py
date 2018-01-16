import build_contentful_data
import dateutil
import json
import os
import requests

from dotenv import load_dotenv
from os.path import join, dirname
from urlparse import urlparse

try:
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
except Exception as e:
    print "\nMissing .env file\n"

EVENTBRITE_OAUTH_TOKEN = os.environ.get('EVENTBRITE_OAUTH_TOKEN', None)

EVENTBRITE_API_BASE = 'https://www.eventbriteapi.com/v3/events/'

class EventbriteSaver():

    def __init__(self, url):
        self.url = url
        self.save_data()

    def get_event_id(self):
        url_components = urlparse(self.url)
        if not url_components.netloc == 'www.eventbrite.com':
            return None

        # hackily parsing eventbrite urls
        event_name = url_components.path.split('/')[-1]
        event_id = event_name.split('-')[-1]
        return event_id

    def save_data(self):
        event_id = self.get_event_id()
        api_url = EVENTBRITE_API_BASE + event_id + '?expand=venue'
        response = requests.get(
            api_url,
            headers = {
                "Authorization": "Bearer %s" % EVENTBRITE_OAUTH_TOKEN,
            },
            verify = True,
        )
        self.title = response.json()['name']['text']
        self.description = response.json()['description']['text']
        self.start_time = dateutil.parser.parse(response.json()['start']['local'])
        self.end_time = dateutil.parser.parse(response.json()['end']['local'])

        lat = float(response.json()['venue']['address']['latitude'])
        lon = float(response.json()['venue']['address']['longitude'])
        name = response.json()['venue']['name']
        room = response.json()['venue']['address']['localized_address_display']
        self.location_id = build_contentful_data.find_location_id(lat, lon, name, room)

if __name__ == '__main__':
    print EventbriteSaver("https://www.eventbrite.com/e/build-products-like-its-day-1-every-day-tickets-34700590400").start_time
