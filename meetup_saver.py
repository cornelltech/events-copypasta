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

        # the meetup api just responds with less fields available if they
        # aren't publicly visible, so we can't rely on the response status_code
        # to tell us whether we have access

        response_contents = response.json()

        if 'name' in response_contents:
            self.title = response.json()['name']
        else:
            raise urllib2.URLError(reason='this event is not visible to our application')

        if 'description' in response_contents:
        # description = response.json()['description']
            self.description = BeautifulSoup(description).get_text()
        else:
            self.description = None

        if ('local_date' in response_contents) \
            and ('local_time' in response_contents) \
            and ('utc_offset' in response_contents):
                date = response_contents['local_date']
                time = response_contents['local_time']
                timezone = response_contents['utc_offset'] / (60 * 60 * 1000)
                self.start_time = dateutil.parser.parse('%s %s %d' % (date, time, timezone)).isoformat()
        else:
            self.start_time = None

        # TODO: temporary placeholder for end_time
        self.end_time = None

        if 'venue' in response_contents:
            lat = float(response.json()['venue']['lat'])
            lon = float(response.json()['venue']['lon'])
            name = response.json()['venue']['name']
            room = response.json()['venue']['address_1']
            self.location_id = build_contentful_data.find_location_id(lat, lon, name, room)
        else:
            self.location_id = None

if __name__ == '__main__':
    m = MeetupSaver("https://www.meetup.com/Elm-NYC/events/245755712/")
