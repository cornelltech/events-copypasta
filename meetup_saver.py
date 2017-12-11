import build_contentful_data
import dateutil
import json
import requests
import urllib2

import pdb

from bs4 import BeautifulSoup
from urlparse import urlparse

MEETUP_URL_BASE = "https://api.meetup.com/%s/events/%s"

class MeetupSaver():

    def __init__(self, url):
        self.url = url
        self.save_data()

    def save_data(self):
        # title, description, start_time, end_time, location_id
        url_components = urlparse(self.url)
        path_elements = url_components.path.split('/')

        group = path_elements[1]
        event_id = path_elements[3]

        api_url = MEETUP_URL_BASE % (group, event_id)

        response = requests.get(
            api_url,
            verify = True,
        )

        self.title = response.json()['name']
        description = response.json()['description']
        self.description = BeautifulSoup(description).get_text()

        date = response.json()['local_date']
        time = response.json()['local_time']
        timezone = response.json()['utc_offset'] / (60 * 60 * 1000)
        self.start_time = dateutil.parser.parse('%s %s %d' % (date, time, timezone)).isoformat()
        self.end_time = None

        lat = float(response.json()['venue']['lat'])
        lon = float(response.json()['venue']['lon'])
        name = response.json()['venue']['name']
        room = response.json()['venue']['address_1']
        self.location_id = build_contentful_data.find_location_id(lat, lon, name, room)

if __name__ == '__main__':
    m = MeetupSaver("https://www.meetup.com/Elm-NYC/events/245755712/")
    print m.title
    print m.description
    print m.start_time
    print m.location_id
