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

from datetime import date
from django.db.models import *
from django.conf import settings
from django.contrib.auth.models import User
from django.template import Context,Template
from django.utils.timezone import now

locale = settings.LOCALE_DATE


def user(name): return User.objects.filter(username=name)[0]
def superuser(): return User.objects.filter(is_superuser=True)[0]

class Profile(Model):
    user = ForeignKey(User,related_name='+', on_delete=CASCADE)
    coins = IntegerField(default=0)
    visual = CharField(default="",max_length=100)
    career = CharField(default='',max_length=50)
    birthday = DateTimeField(default=now)
    google_token = TextField(default="",max_length=120)
    twitter_token = TextField(default="",max_length=120)
    facebook_token = TextField(default="",max_length=120)
    bio = TextField(default='',max_length=140)
    date = DateTimeField(auto_now_add=True)
    def years_old(self): return datetime.timedelta(self.birthday,date.today)
    def token(self): return ''
    def get_username(self): return self.user.username
    def month(self): return locale[self.date.month-1]

class Followed(Model):
    followed = IntegerField(default=1)
    follower = IntegerField(default=2)
    date = DateTimeField(auto_now_add=True)

Profile.year = property(lambda p: p.years_old())
Profile.name = property(lambda p: p.get_username())
User.profile = property(lambda u: Profile.objects.get_or_create(user=u)[0])
