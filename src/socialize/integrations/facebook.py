"""Facebook social plugin for the socialize app."""
#!/usr/bin/python
# pylint: disable=E1101
#
# This file is part of django-socialize project.
#
# Copyright (C) 2010-2025 William Oliveira de Lagos <william.lagos@icloud.com>
#
# Socialize is free software: you can redistribute it and/or modify
# it under the terms of the Lesser GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Socialize is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Socialize. If not, see <http://www.gnu.org/licenses/>.
#

import json
import time
import datetime
import urllib.parse
import urllib.request

FACEBOOK_GRAPH_API = 'https://graph.facebook.com'


class FacebookSocialPlugin:
    """Facebook social plugin for the socialize app."""

    def __init__(self, token):
        self.access_token = token
        self.base_url = FACEBOOK_GRAPH_API

    def update_status(self, content):
        """Updates the user's Facebook status."""
        data = {
            'message': f'{content}'.encode('utf-8')
        }

        self.graph_request('/me/feed', data)
        return 'Published posting successfully on Facebook'

    def send_event(self, name, start_time, description, location, ticket_uri):
        """Sends an event to the user's Facebook account."""
        data = {
            'name': name.encode('utf-8'),
            'start_time': self.convert_datetime(start_time).strftime('%Y-%m-%dT%H:%M:%S').encode('utf-8'),
            'description': description.encode('utf-8'),
            'location': location.encode('utf-8'),
            'ticket_uri': ticket_uri
        }

        response = self.graph_request('/me/events', data)
        event_id = json.loads(response).get('id')
        return event_id

    def send_event_cover(self, event_id, photo_url):
        """Sends a cover image to the user's Facebook event."""
        self.graph_request(f'{event_id}', {'cover_url': photo_url})
        return 'Published image cover on event successfully on Facebook'

    def convert_datetime(self, date_value):
        """Converts a date string to a datetime object."""
        d = time.strptime(date_value, '%d/%m/%Y')
        return datetime.datetime.fromtimestamp(time.mktime(d))

    def graph_request(self, url, data):
        """Sends a POST request to the Facebook API."""
        full_url = f'{self.base_url}{url}'
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        encoded_data = urllib.parse.urlencode(data).encode('utf-8')
        request = urllib.request.Request(
            full_url, data=encoded_data, headers=headers)

        try:
            with urllib.request.urlopen(request) as response:
                response_data = response.read().decode('utf-8')
                return response_data
        except urllib.error.URLError as e:
            return json.dumps({'error': str(e)})
