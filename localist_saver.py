import build_contentful_data
import dateutil
import json
import requests
import urllib2

import pdb

from bs4 import BeautifulSoup

CORNELL_API_BASE = 'http://events.cornell.edu/api/2/events/'

class LocalistSaver():

    def __init__(self, url):
        self.url = url
        self.save_data()

    def save_data(self):
        # find event id
        result = requests.get(self.url)
        if result.status_code == 200:
            soup = BeautifulSoup(result.content, "lxml")
            event_id = soup.find("meta", {"name": "localist-event-id"})['content']

            event_api_url = CORNELL_API_BASE + event_id
            event_api_response = requests.get(event_api_url)

            event_content = json.loads(event_api_response.content)['event']

            self.title = event_content['title']

            description = event_content['description']
            self.description = BeautifulSoup(description).get_text()

            # TODO: figure out how to deal with a series of events better than this
            # (right now it only inputs the first event in the series)
            series = event_content['event_instances']
            first_event = series[0]['event_instance']
            self.start_time = dateutil.parser.parse(first_event['start'])
            self.end_time = dateutil.parser.parse(first_event['end'])

            # location
            address = event_content['location']
            room = event_content['room_number']
            if address:
                (lat, lon) = build_contentful_data.get_latlong_from_address(address)
                self.location_id = build_contentful_data.find_location_id(lat, lon, address, room)
            else:
                self.location_id = None
        else:
            raise urllib2.URLError(reason='page does not exist')

if __name__ == '__main__':
    local = LocalistSaver("http://events.cornell.edu/event/the_martin_luther_king_jr_day_of_commemoration_featuring_keynote_speaker_mitchell_s_jackson")
