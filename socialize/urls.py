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

from django.conf.urls import url,include
from django.urls import path

from .views import *

urlpatterns = [
    path('', AccountsView.as_view()),
    # url(r'^profile', profile),
    # url(r'^enter', authenticate),
    # url(r'^leave', leave),
    # url(r'^delete', delete),
    # url(r'^userid', ids),
    # url(r'^search', search),
    # url(r'^explore', search),
    # url(r'^known', explore),
    # url(r'^following', following),
    # url(r'^follow', follow),
    # url(r'^unfollow', unfollow),
    # url(r'^twitter/post', twitter_post),
    # url(r'^facebook/post', facebook_post),
    # url(r'^facebook/eventcover', facebook_eventcover),
    # url(r'^facebook/event', facebook_event),
    # url(r'^participate', participate),
    # url(r'^tutorial', tutorial),
    # url(r'^discharge', discharge),
    # url(r'^recharge', recharge),
    # url(r'^balance', balance),
]
