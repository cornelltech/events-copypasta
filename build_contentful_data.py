import contentful
import contentful_management
import json
import os
import pdb
import requests

from contentful import Client
from contentful_management import Client
from os.path import join, dirname
from dotenv import load_dotenv
from time import sleep

try:
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
except Exception as e:
    print "\nMissing .env file\n"

# contentful space data
SPACE_ID = os.environ.get('SPACE_ID', None)
MGMT_TOKEN = os.environ.get('MANAGEMENT_TOKEN', None)
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN', None)
GOOGLE_GEOCODING_TOKEN = os.environ.get('GOOGLE_GEOCODING_TOKEN', None)

def get_latlong_from_address(address):
    GOOGLE_GEOCODE_BASE = 'https://maps.googleapis.com/maps/api/geocode/json?key=%s&address=' % GOOGLE_GEOCODING_TOKEN
    url = GOOGLE_GEOCODE_BASE + address
    response = requests.get(url)

    json_data = json.loads(response.content)
    json_latlong = json_data['results'][0]['geometry']['location']
    lat = float(json_latlong['lat'])
    lon = float(json_latlong['lng'])

    return (lat, lon)


def get_locations():
    delivery_client = contentful.Client(SPACE_ID, ACCESS_TOKEN)
    return delivery_client.entries({'content_type': 'location'}).items

def get_tags():
    delivery_client = contentful.Client(SPACE_ID, ACCESS_TOKEN)
    return delivery_client.entries({'content_type': 'tag'}).items

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
    # loc.publish()
    return loc.sys['id']

def find_tag_id(name):
    delivery_client = contentful.Client(SPACE_ID, ACCESS_TOKEN)
    tag_results = delivery_client.entries({'content_type': 'tag',
                                            'fields.title': name})
    if tag_results:
        return tag_results[0].id
    else:
        new_tag = build_tag(name)
        new_tag = send_to_contentful(new_tag)
        return new_tag.id

def build_field(name, contents):
    if contents:
        return {name: {'en-US': contents}}
    else:
        return

# complicated formatting
def build_location_link(id):
    return {'en-US': [{'sys': {'linkType': 'Entry', 'type': 'Link', 'id': id}}]}

def build_tag_link(id):
    return {'sys': {'linkType': 'Entry', 'type': 'Link', 'id': id}}


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
                external_url=None, location_id=None, category=None, tags=None):
    fields_data = []
    fields_data.append(build_field('eventTitle', title))
    fields_data.append(build_field('startTime', start_time))
    fields_data.append(build_field('endTime', end_time))
    fields_data.append(build_field('description', description))
    fields_data.append(build_field('externalUrl', external_url))
    fields_data.append(build_field('category', category))
    fields_data.append({'locationObject': build_location_link(location_id)})

    tag_links_list = []
    for tag in tags:
        tag_link = build_tag_link(find_tag_id(tag.strip()))
        tag_links_list.append(tag_link)

    if tag_links_list:
        fields_data.append(build_field('tags', tag_links_list))

    # construct json for all the fields
    fields = {}
    for field in fields_data:
        if field:
            fields.update(field)
    return {'content_type_id': 'event', 'fields': fields}

def build_tag(title):
    fields = build_field('title', title)
    return {'content_type_id': 'tag', 'fields': fields}

def send_to_contentful(attributes):
    mgmt_client = contentful_management.Client(MGMT_TOKEN)
    new_entry = mgmt_client.entries(SPACE_ID).create(None, attributes)
    new_entry.publish()
    return new_entry

def get_categories():
    # categories = ['talk',
    #                 'conference',
    #                 'recruitment',
    #                 'showcase',
    #                 'discussion',
    #                 'hackathon']
    # return categories

    # this is sort of hacky, but there isn't a clean way to get them out
    mgmt_client = contentful_management.Client(MGMT_TOKEN)
    types = mgmt_client.content_types(SPACE_ID)
    event = types.find('event')
    for f in event.fields:
        if f.id == 'category':
            return f.validations[0].raw['in']

if __name__ == '__main__':
    # lat, lon, name, room
    lat = 40.740914
    lon = -74.00218100000001
    name = 'The Foundry'
    room = '#802'
    #
    tags = 'july, august, september'
    if tags:
        tags = tags.split(',')
    entry_attributes = build_event('party friday',
                                    start_time='2017-06-27T19:00:00-04:00',
                                    description='it is friday let\'s party!',
                                    location_id=find_location_id(lat, lon, name, room),
                                    category='talk', tags=tags)

    entry = send_to_contentful(entry_attributes)
