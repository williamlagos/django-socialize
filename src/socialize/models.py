"""Models for the social network."""

# !/usr/bin/python
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

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now


class Actor(models.Model):
    """Represents an actor in the social network (local or federated)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    actor_url = models.URLField(max_length=500, blank=True, null=True, unique=True)
    username = models.CharField(max_length=150, blank=True, default="")
    domain = models.CharField(max_length=255, blank=True, default="")
    display_name = models.CharField(max_length=255, blank=True, null=True)
    inbox = models.URLField(max_length=500, blank=True, null=True)
    outbox = models.URLField(max_length=500, blank=True, null=True)
    shared_inbox = models.URLField(max_length=500, blank=True, null=True)
    followers_url = models.URLField(max_length=500, blank=True, null=True)
    following_url = models.URLField(max_length=500, blank=True, null=True)
    actor_type = models.CharField(max_length=50, default="Person")
    public_key = models.TextField(blank=True, default="")
    score = models.IntegerField(default=0)

    joined_at = models.DateTimeField(auto_now_add=True)
    bio = models.TextField(default="", max_length=140, blank=True)
    title = models.CharField(default="", max_length=50, blank=True)
    birthdate = models.DateTimeField(default=now)

    def years_old(self):
        """Returns the age of the actor."""
        return datetime.timedelta(self.birthdate, datetime.date.today)

    def get_username(self):
        """Returns the username for the actor."""
        if self.user and self.user.username:
            return self.user.username
        return self.username

    def get_domain(self):
        """Returns the domain for the actor."""
        if self.domain:
            return self.domain
        return getattr(settings, "SITE_DOMAIN", "localhost:8000")

    def get_actor_url(self):
        """Returns the canonical ActivityPub URL of the actor."""
        if self.actor_url:
            return self.actor_url
        uname = self.get_username()
        dom = self.get_domain()
        if uname:
            return f"https://{dom}/users/{uname}/"
        return f"https://{dom}/actors/{self.id}/"

    def get_inbox_url(self):
        """Returns the inbox URL of the actor."""
        if self.inbox:
            return self.inbox
        return f"{self.get_actor_url()}inbox/"

    def get_outbox_url(self):
        """Returns the outbox URL of the actor."""
        if self.outbox:
            return self.outbox
        return f"{self.get_actor_url()}outbox/"

    def get_followers_url(self):
        """Returns the followers collection URL of the actor."""
        if self.followers_url:
            return self.followers_url
        return f"{self.get_actor_url()}followers/"

    def get_following_url(self):
        """Returns the following collection URL of the actor."""
        if self.following_url:
            return self.following_url
        return f"{self.get_actor_url()}following/"

    def get_shared_inbox_url(self):
        """Returns the shared inbox URL."""
        if self.shared_inbox:
            return self.shared_inbox
        dom = self.get_domain()
        return f"https://{dom}/inbox/"

    def get_display_name(self):
        """Returns the display name of the actor."""
        if self.display_name:
            return self.display_name
        if self.user:
            full = f"{self.user.first_name} {self.user.last_name}".strip()
            if full:
                return full
            return self.user.username
        return self.username

    def get_user_permissions(self):
        """Returns the permissions of the actor."""
        if self.user:
            return self.user.get_user_permissions()
        return set()

    def as_activitypub(self):
        """Returns the actor as an ActivityPub object."""
        actor_url = self.get_actor_url()
        data = {
            "@context": [
                "https://www.w3.org/ns/activitystreams",
                "https://w3id.org/security/v1",
            ],
            "id": actor_url,
            "type": self.actor_type,
            "preferredUsername": self.get_username(),
            "name": self.get_display_name(),
            "summary": self.bio,
            "inbox": self.get_inbox_url(),
            "outbox": self.get_outbox_url(),
            "followers": self.get_followers_url(),
            "following": self.get_following_url(),
            "endpoints": {
                "sharedInbox": self.get_shared_inbox_url(),
            },
        }
        if self.public_key:
            data["publicKey"] = {
                "id": f"{actor_url}#main-key",
                "owner": actor_url,
                "publicKeyPem": self.public_key,
            }
        return data


class Follow(models.Model):
    """Represents a follow relationship between actors."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey(
        Actor, on_delete=models.CASCADE, related_name="following_set"
    )
    target = models.ForeignKey(
        Actor, on_delete=models.CASCADE, related_name="followers_set"
    )
    accepted = models.BooleanField(default=True)
    activity_id = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta options for Follow."""

        unique_together = ("actor", "target")
        verbose_name = "Follow"
        verbose_name_plural = "Follows"

    def __str__(self):
        return f"{self.actor.get_username()} follows {self.target.get_username()}"


class Object(models.Model):
    """Represents an object in the social network (Note, Article, Video, Audio, Image)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    object_url = models.URLField(max_length=500, blank=True, null=True, unique=True)
    object_type = models.CharField(max_length=50, default="Note")
    summary = models.TextField(blank=True, default="")
    content = models.TextField(blank=True, default="")
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE)
    attachment = models.JSONField(default=list, blank=True)
    published_at = models.DateTimeField(auto_now_add=True)

    def get_object_url(self):
        """Returns the canonical URL of the object."""
        if self.object_url:
            return self.object_url
        dom = getattr(settings, "SITE_DOMAIN", "localhost:8000")
        return f"https://{dom}/objects/{self.id}/"

    def as_activitypub(self):
        """Returns the object as an ActivityPub object."""
        data = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "id": self.get_object_url(),
            "type": self.object_type,
            "published": self.published_at.isoformat(),
            "attributedTo": self.actor.get_actor_url(),
            "to": ["https://www.w3.org/ns/activitystreams#Public"],
            "content": self.content,
        }
        if self.summary:
            data["summary"] = self.summary
        if self.attachment:
            data["attachment"] = self.attachment
        return data


class Activity(models.Model):
    """Represents an activity in the social network (Create, Like, Follow, Announce, Undo)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    activity_url = models.URLField(max_length=500, blank=True, null=True)
    activity_type = models.CharField(max_length=50)
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE)
    object_data = models.JSONField()
    published_at = models.DateTimeField(auto_now_add=True)

    def get_activity_url(self):
        """Returns the URL of the activity."""
        if self.activity_url:
            return self.activity_url
        dom = getattr(settings, "SITE_DOMAIN", "localhost:8000")
        return f"https://{dom}/activities/{self.id}/"

    def as_activitypub(self):
        """Returns the activity as an ActivityPub object."""
        if isinstance(self.object_data, dict) and "@context" in self.object_data:
            return self.object_data
        return {
            "@context": "https://www.w3.org/ns/activitystreams",
            "id": self.get_activity_url(),
            "type": self.activity_type,
            "actor": self.actor.get_actor_url(),
            "object": self.object_data,
            "published": self.published_at.isoformat(),
        }


class Vault(models.Model):
    """Represents a vault with its access keys in the social network."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE)
    private_key = models.TextField()

    class Meta:
        """Meta options for the Vault model."""

        verbose_name = "Vault"
        verbose_name_plural = "Vaults"


class Token(models.Model):
    """Represents an OAuth standard token in the social network."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255, unique=True, default=uuid.uuid4)
    expires_at = models.DateTimeField(default=now() + datetime.timedelta(hours=1))

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
