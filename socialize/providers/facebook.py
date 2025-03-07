"""Facebook social provider for the socialize app."""
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

# TODO: Revamp this social provider considering the latest changes in the Facebook API.

import json
import time
import re
import logging

from datetime import datetime
from time import mktime, strptime

from django.http import HttpResponse as response
from django.http import HttpResponseRedirect as redirect
from django.shortcuts import render
from django.db import IntegrityError
from django.contrib.auth.models import AnonymousUser, User
from django.conf import settings
from django.shortcuts import render


class FacebookSocialProvider:

    def update_status(self, request):
        u = self.current_user(request)
        token = u.profile.facebook_token
        text = str('%s' % request.GET['content'])
        data = {'message': text.encode('utf-8')}
        if 'id' in request.REQUEST:
            url = '/%s/feed' % request.REQUEST['id']
        else:
            url = '/me/feed'
        self.oauth_post_request(url, token, data, 'facebook')
        return response('Published posting successfully on Facebook')

    def send_event(self, request):
        u = self.current_user(request)
        token = u.profile.facebook_token
        name = dates = descr = local = value = ''
        for k, v in request.REQUEST.items():
            if 'name' in k:
                name = v.encode('utf-8')
            elif 'deadline' in k:
                dates = v
            elif 'description' in k:
                descr = v.encode('utf-8')
            elif 'location' in k:
                local = v.encode('utf-8')
            elif 'value' in k:
                value = v
        date = self.convert_datetime(dates)
        url = 'http://%s/Socialize/basket?alt=redir&id=%s&value=%s&token=@@' % (
            settings.Socialize_URL, value, name)
        data = {'name': name, 'start_time': date,
                'description': descr, 'location': local, 'ticket_uri': url}
        id = json.loads(self.oauth_post_request(
            "/me/events", token, data, 'facebook'))['id']
        return response(id)

    def send_event_cover(self, request):
        u = self.current_user(request)
        token = u.profile.facebook_token
        ident = request.REQUEST['id']
        photo = request.REQUEST['url']
        self.oauth_post_request('/%s' % ident, token,
                                {'cover_url': photo}, 'facebook')
        return response('Published image cover on event successfully on Facebook')

    def convert_datetime(self, date_value):
        """Converts a date string to a datetime object."""
        d = time.strptime(date_value, '%d/%m/%Y')
        return datetime.fromtimestamp(time.mktime(d))
