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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=255, blank=True, null=True)
    inbox = models.URLField(blank=True, null=True)
    outbox = models.URLField(blank=True, null=True)
    actor_type = models.CharField(max_length=50, default='Person')
    public_key = models.TextField()
    score = models.IntegerField(default=0)

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

    def get_display_name(self):
        """Returns the display name of the actor."""
        return f'{self.user.first_name} {self.user.last_name}'.strip()

    def get_user_permissions(self):
        """Returns the permissions of the actor."""
        return self.user.get_user_permissions()

    def as_activitypub(self):
        """Returns the actor as an ActivityPub object."""
        return {
            '@context': 'https://www.w3.org/ns/activitystreams',
            'name': self.get_display_name() or self.user.username,
            'id': self.get_actor_url(),
            'type': self.actor_type,
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
    private_key = models.TextField()

    class Meta:
        """Meta options for the Vault model."""
        verbose_name = 'Vault'
        verbose_name_plural = 'Vaults'


class Token(models.Model):
    """Represents an OAuth standard token in the social network. (e.g. Access, Refresh)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    access_token = models.CharField(
        max_length=255, unique=True, default=uuid.uuid4)
    expires_at = models.DateTimeField(
        default=now() + datetime.timedelta(hours=1))

    def is_valid(self):
        """Returns whether the token is still valid."""
        return now() < self.expires_at

    def refresh(self):
        """Refreshes the token and returns the new access token."""
        self.access_token = uuid.uuid4()
        self.expires_at = now() + datetime.timedelta(hours=1)
        self.save()
        return self.access_token


def user(name):
    """Returns the user with the given username."""
    return User.objects.filter(username=name)[0]


def superuser():
    """Returns the first superuser in the database."""
    return User.objects.filter(is_superuser=True)[0]


Actor.year = property(lambda p: p.years_old())
Actor.name = property(lambda p: p.get_username())
