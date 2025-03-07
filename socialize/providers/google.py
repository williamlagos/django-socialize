"""Google social provider for the socialize app."""
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

# TODO: Revamp this social provider considering the latest changes in the Google/YouTube API.

import json
import urllib
from io import StringIO
from xml.dom.minidom import parseString

from django.conf import settings

try:
    import gdata.youtube
    import gdata.media
except ImportError as e:
    pass

# apis = json.load(open('settings.json','r'))
# google_api = apis['social']['google']
google_api = ('', '')


class GoogleSocialProvider:

    def __init__(self):
        self.developer_key = settings.GOOGLE_API_KEY
        self.client_id = settings.GOOGLE_CLIENT_ID

    def videos_by_user(self, username):
        uri = 'https://gdata.youtube.com/feeds/api/users/%s/uploads?alt=json' % username
        return self.do_request(uri)

    def video_thumbnail(self, token, access_token):
        actoken = self.refresh_google_token(access_token)
        uri = 'https://gdata.youtube.com/feeds/api/users/default/uploads/%s?access_token=%s' % (
            token, actoken)
        thumbnail = parseString(self.do_request(uri)).getElementsByTagName(
            'media:thumbnail')[0].attributes['url'].value
        return str(thumbnail)

    def video_entry(self, title, description, keywords, access_token):
        media_group = gdata.media.Group(title=gdata.media.Title(text=title),
                                        description=gdata.media.Description(
                                            description_type='plain', text=description),
                                        keywords=gdata.media.Keywords(
                                            text='efforia'),
                                        category=[gdata.media.Category(text='Entertainment',
                                                                       scheme='http://gdata.youtube.com/schemas/2007/categories.cat',
                                                                       label='Entertainment')],
                                        player=None)
        # private=gdata.media.Private())
        video_entry = gdata.youtube.YouTubeVideoEntry(media=media_group)
        url, token = self.get_upload_token(video_entry, access_token)
        return url, token

    def get_upload_token(self, video_entry, access_token):
        actoken = self.refresh_google_token(access_token)
        print(actoken)
        headers = {
            'Authorization': 'OAuth %s' % actoken,
            'X-gdata-key': 'key=%s' % self.developer_key,
            'Content-type': 'application/atom+xml'
        }
        response = self.do_request(
            'https://gdata.youtube.com/action/GetUploadToken', str(video_entry), headers)
        print(response)
        url = parseString(response).getElementsByTagName(
            'url')[0].childNodes[0].data
        token = parseString(response).getElementsByTagName(
            'token')[0].childNodes[0].data
        return url, token

    def search_video(self, search_terms):
        pass

    def do_request(self, url, data=None, headers=None):
        """Do a request"""
        request = urllib.request.Request(url=url, data=data, headers=headers)
        try:
            request_open = urllib.request.urlopen(request)
            response = request_open.read()
            request_open.close()
        except urllib.error.HTTPError as e:
            print(url)
            print(data)
            print(headers)
            print(e.code)
            print(e.msg)
            print(e.hdrs)
            print(e.fp)
        return response
