import contentful
import contentful_management
import os
import pdb

from contentful import Client
from contentful_management import Client
from os.path import join, dirname
from dotenv import load_dotenv

try:
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
except Exception as e:
    print "\nMissing .env file\n"

# contentful space data
SPACE_ID = os.environ.get('SPACE_ID', None)
MGMT_TOKEN = os.environ.get('MANAGEMENT_TOKEN', None)
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN', None)

def get_locations():
    client = contentful.Client(SPACE_ID, ACCESS_TOKEN)
    return client.entries({'content_type': 'location'}).items

# creates new location if none exists yet
def find_location_id(lat, lon, name, room):
    locations = get_locations()
    for location in locations:
        if location.address.lat == lat:
            if location.address.lon == lon:
                if location.name == name:
                    if location.room == room:
                        return location.sys['id']
    # if it doesn't exist, create it
    new_location = build_location(lat, lon, name, room)
    print new_location
    loc = send_to_contentful(new_location)
    loc.publish()
    return loc.sys['id']

def build_field(name, contents):
    if contents:
        return {name: {'en-US': contents}}
    else:
        return

# complicated formatting
def build_location_link(location_id):
    return {'en-US': [{'sys': {'linkType': 'Entry', 'type': 'Link', 'id': location_id}}]}

def build_location(lat, lon, name, room):
    fields_data = []
    fields_data.append(build_field('name', name))
    fields_data.append(build_field('room', room))
    fields_data.append(build_field('address', {'lat': lat, 'lon': lon}))
    fields = {}
    for field in fields_data:
        fields.update(field)
    return {'content_type_id': 'location', 'fields': fields}

def build_event(title, start_time=None, end_time=None, description=None,
                external_url=None, location_id=None):
    fields_data = []
    fields_data.append(build_field('eventTitle', title))
    fields_data.append(build_field('startTime', start_time))
    fields_data.append(build_field('endTime', end_time))
    fields_data.append(build_field('description', description))
    fields_data.append(build_field('externalUrl', external_url))
    fields_data.append({'locationObject': build_location_link(location_id)})
    fields = {}
    for field in fields_data:
        if field:
            fields.update(field)
    return {'content_type_id': 'event', 'fields': fields}

def build_tag(title):
    fields = build_field('title', title)
    return {'content_type_id': 'tag', 'fields': fields}

def send_to_contentful(attributes):
    client = contentful_management.Client(MGMT_TOKEN)
    new_entry = client.entries(SPACE_ID).create(None, attributes)
    return new_entry

if __name__ == '__main__':
    # lat, lon, name, room
    lat = 40.740914
    lon = -74.00218100000001
    name = 'The Foundry'
    room = '#802'
    entry_attributes = build_event('party friday',
                                    start_time='2017-06-27T19:00:00-04:00',
                                    description='it is friday let\'s party!',
                                    location_id=find_location_id(lat, lon, name, room))

    print entry_attributes
    send_to_contentful(entry_attributes)
