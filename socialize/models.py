#!/usr/bin/python
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

import datetime
import uuid

from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


class Actor(models.Model):
    """Represents an actor in the social network. (e.g. Person, Group)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=255, blank=True, null=True)
    inbox = models.URLField(blank=True, null=True)
    outbox = models.URLField(blank=True, null=True)
    actor_type = models.CharField(max_length=50, default='Person')

    joined_at = models.DateTimeField(auto_now_add=True)
    bio = models.TextField(default='', max_length=140)
    title = models.CharField(default='', max_length=50)
    birthdate = models.DateTimeField(default=now)

    def years_old(self):
        """Returns the age of the actor."""
        return datetime.timedelta(self.birthdate, datetime.date.today)


class Activity(models.Model):
    """Represents an activity in the social network. (e.g. Post, Like, Follow)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Create, Update, Delete, Follow, Like, Block, Undo
    activity_type = models.CharField(max_length=50)
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE)
    object_data = models.JSONField()  # Stores activity object data as JSON.
    published_at = models.DateTimeField(auto_now_add=True)


class Object(models.Model):
    """Represents an object in the social network. (e.g. Post, Image, Video)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    object_type = models.CharField(max_length=50, default='Note')
    content = models.TextField()
    actor = models.ForeignKey(User, on_delete=models.CASCADE)
    published_at = models.DateTimeField(auto_now_add=True)


class Vault(models.Model):
    """Represents an actor vault with its access keys in the social network. (e.g. Password, Tokens)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE)
    access_key = models.CharField(max_length=255)
    secret_key = models.CharField(max_length=255)
    # TODO: Add any e-commerce related fields to another package.
    # coins = IntegerField(default=0)

    # TODO: Consider moving these sensitive fields and functions to another model/table.
    # google_token = models.TextField(default="", max_length=120)
    # twitter_token = models.TextField(default="", max_length=120)
    # facebook_token = models.TextField(default="", max_length=120)
    # def token(self):
    #     return self.google_token or self.twitter_token or self.facebook_token
    created_at = models.DateTimeField(auto_now_add=True)


def user(name):
    """Returns the user with the given username."""
    return User.objects.filter(username=name)[0]


def superuser():
    """Returns the first superuser in the database."""
    return User.objects.filter(is_superuser=True)[0]


Actor.year = property(lambda p: p.years_old())
Actor.name = property(lambda p: p.get_username())
