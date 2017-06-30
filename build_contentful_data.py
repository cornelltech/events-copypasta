import os
import pdb

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

def build_field(name, contents):
    if contents:
        return {name: {'en-US': contents}}
    else:
        return

def build_event(title, startTime=None, description=None, external_url=None):
    fields_data = []
    fields_data.append(build_field('eventTitle', title))
    fields_data.append(build_field('startTime', startTime))
    fields_data.append(build_field('description', description))
    fields_data.append(build_field('externalUrl', external_url))
    fields = {}
    for field in fields_data:
        if field:
            fields.update(field)
    return {'content_type_id': 'event', 'fields': fields}

def build_tag(title):
    fields = build_field('title', title)
    return {'content_type_id': 'tag', 'fields': fields}

def send_event_to_contentful(event_attributes):
    client = Client(MGMT_TOKEN)
    new_entry = client.entries(SPACE_ID).create(None, event_attributes)


if __name__ == '__main__':
    entry_attributes = build_event('party friday',
                                    startTime='2017-06-27T19:00:00-04:00',
                                    description='it is friday let\'s party!')

    send_event_to_contentful(entry_attributes)
