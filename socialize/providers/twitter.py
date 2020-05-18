#!/usr/bin/python
#
# This file is part of django-socialize project.
#
# Copyright (C) 2011-2020 William Oliveira de Lagos <william.lagos@icloud.com>
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
import urllib
import re
import logging

from datetime import datetime
from time import mktime,strptime

from django.http import HttpResponse as response
from django.http import HttpResponseRedirect as redirect
from django.shortcuts import render
from django.db import IntegrityError
from django.contrib.auth.models import AnonymousUser, User
from django.conf import settings
from django.shortcuts import render

class Twitter(Socialize):
    def update_status(self,request):
        u = self.current_user(request)
        if len(request.GET['content']) > 137: 
            short = str('%s...' % (request.GET['content'][:137]))
        else: short = str('%s' % (request.GET['content']))
        tokens = u.profile.twitter_token
        if not tokens: tokens = self.own_access()['twitter_token']
        data = {'status':short.encode('utf-8')}
        self.oauth_post_request('/statuses/update.json',tokens,data,'twitter')
        return response('Published posting successfully on Twitter')
