import build_contentful_data
import eventsaver
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

class EventbriteSaver(eventsaver.EventSaver):

    def __init__(self, url):
        super(EventbriteSaver, self).__init__(url)
        self.save_eventbrite_data()

    def get_event_id(self):
        url_components = urlparse(self.url)
        if not url_components.netloc == 'www.eventbrite.com':
            return None

        # hackily parsing eventbrite urls
        event_name = url_components.path.split('/')[-1]
        event_id = event_name.split('-')[-1]
        return event_id

    def save_eventbrite_data(self):
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
        self.start_time = response.json()['start']['local']
        self.end_time = response.json()['end']['local']

        lat = float(response.json()['venue']['address']['latitude'])
        lon = float(response.json()['venue']['address']['longitude'])
        name = response.json()['venue']['name']
        room = response.json()['venue']['address']['localized_address_display']
        self.location_id = build_contentful_data.find_location_id(lat, lon, name, room)

    def get_title(self):
        return self.title

    def get_start_time(self):
        return self.start_time

    def get_end_time(self):
        return self.end_time

    def get_description(self):
        return self.description

    def get_location(self):
        return self.location_id

    def print_info(self):
        print self.get_start_time()
        print self.get_end_time()
        print self.get_url()
        print self.get_description()
        print self.get_location()

if __name__ == '__main__':
    url = 'https://www.eventbrite.com/e/ckgsb-knowledge-series-event-expanding-asia-opportunities-and-challenges-of-corporate-social-tickets-39089636154'
    esaver = EventbriteSaver(url)
    print esaver.get_start_time()
    print esaver.get_end_time()
    print esaver.get_url()
    print esaver.get_description()
