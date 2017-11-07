import build_contentful_data
import eventsaver
import json
import requests

import pdb

from bs4 import BeautifulSoup

CORNELL_API_BASE = 'http://events.cornell.edu/api/2/events/'

class LocalistSaver(eventsaver.EventSaver):

    def __init__(self, url):
        super(LocalistSaver, self).__init__(url)
        self.save_localist_data()

    def save_localist_data(self):
        # find event id
        result = requests.get(self.url)
        soup = BeautifulSoup(result.content, "lxml")
        event_id = soup.find("meta", {"name": "localist-event-id"})['content']

        event_api_url = CORNELL_API_BASE + event_id
        event_api_response = requests.get(event_api_url)

        event_content = json.loads(event_api_response.content)['event']

        self.title = event_content['title']

        # TODO: strip out html
        self.description = event_content['description']

        # TODO: figure out how to deal with a series of events better than this
        # (right now it only inputs the first event in the series)
        series = event_content['event_instances']
        first_event = series[0]['event_instance']
        self.start_time = first_event['start']
        self.end_time = first_event['end']

        # location
        address = event_content['location']
        room = event_content['room_number']
        if address:
            (lat, lon) = build_contentful_data.get_latlong_from_address(address)
            self.location_id = build_contentful_data.find_location_id(lat, lon, address, room)
        else:
            self.location_id = ''

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
    url = 'http://events.cornell.edu/event/island_immersion_diving_into_discovery_at_shoals_marine_lab'
    esaver = LocalistSaver(url)
    print esaver.get_start_time()
    print esaver.get_end_time()
    print esaver.get_url()
    print esaver.get_description()
