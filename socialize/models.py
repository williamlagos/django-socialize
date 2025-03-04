"""Models for the social network."""
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

    def get_actor_url(self):
        """Returns the URL of the actor."""
        return f'/actors/{self.id}'

    def as_activitypub(self):
        """Returns the actor as an ActivityPub object."""
        return {
            '@context': 'https://www.w3.org/ns/activitystreams',
            'id': self.get_actor_url(),
            'type': self.actor_type,
            'name': self.display_name or self.username,
            'summary': self.bio,
            'inbox': self.inbox,
            'outbox': self.outbox,
        }


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
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE)
    published_at = models.DateTimeField(auto_now_add=True)

    def get_object_url(self):
        """Returns the URL of the object."""
        return f'/objects/{self.id}'

    def as_activitypub(self):
        """Returns the object as an ActivityPub object."""

        return {
            '@context': 'https://www.w3.org/ns/activitystreams',
            'type': self.object_type,
            'content': self.content,
            'actor': self.actor.get_actor_url(),
            'id': self.get_object_url(),
        }


class Vault(models.Model):
    """Represents a vault with its access keys in the social network. (e.g. Password, Tokens)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE)
    access_key = models.CharField(max_length=255)
    secret_key = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    # TODO: Consider moving these sensitive fields and functions to another model/table.
    # google_token = models.TextField(default="", max_length=120)
    # twitter_token = models.TextField(default="", max_length=120)
    # facebook_token = models.TextField(default="", max_length=120)
    # def token(self):
    #     return self.google_token or self.twitter_token or self.facebook_token

    # TODO: Add any e-commerce related fields to another package.
    # coins = IntegerField(default=0)


def user(name):
    """Returns the user with the given username."""
    return User.objects.filter(username=name)[0]


def superuser():
    """Returns the first superuser in the database."""
    return User.objects.filter(is_superuser=True)[0]


Actor.year = property(lambda p: p.years_old())
Actor.name = property(lambda p: p.get_username())
