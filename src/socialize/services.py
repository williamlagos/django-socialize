"""Services for the socialize app."""
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
import requests

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.conf import settings

from .models import Actor, Activity, Object, Vault, Token


class ActorService:
    """Handles ActivityPub Actor endpoints."""

    def get_actor(self, _, username, as_activitypub=True):
        """Returns the ActivityPub representation of an Actor for the given username."""
        actor = get_object_or_404(Actor, user__username=username)
        if as_activitypub:
            return JsonResponse(actor.as_activitypub())
        return JsonResponse({
            'id': actor.id,
            'username': actor.user.username,
            'display_name': actor.get_display_name(),
            'actor_type': actor.actor_type,
            'bio': actor.bio,
            'title': actor.title,
            'birthdate': actor.birthdate,
            'inbox': actor.inbox,
            'outbox': actor.outbox,
            'permissions': actor.get_user_permissions(),
            'score': actor.score,
            'created_at': actor.created_at,
            'updated_at': actor.updated_at,
        })

    def create_actor(self, data):
        """Creates a new Actor from the given data."""
        private_key, public_key = self.generate_keys()
        user, _ = User.objects.get_or_create(username=data.get('username'))
        actor = Actor.objects.create(user=user, public_key=public_key)
        Vault.objects.create(actor=actor, private_key=private_key)

        return actor

    def generate_keys(self):
        """Generates a new private/public key pair."""
        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048)

        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )

        public_pem = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        return private_pem.decode(), public_pem.decode()

    def get_webfinger(self, request):
        """Returns the WebFinger data request for the user discovery."""
        resource = request.GET.get('resource')
        if resource.startswith('acct:'):
            username = resource.split('acct:')[1].split('@')[0]
            actor = get_object_or_404(Actor, user__username=username)

            return JsonResponse({
                'subject': f'acct:{actor.user.username}@{settings.SITE_DOMAIN}',
                'links': [{
                    'rel': 'self',
                    'type': 'application/activity+json',
                    'href': actor.get_actor_url()
                }]
            })

        return JsonResponse({'error': 'Invalid WebFinger request'}, status=400)


class ActivityService:
    """Handles ActivityPub Activity endpoints for inbox and outbox."""

    def create_activity(self, request, username):
        """Handles ActivityPub inbox messages."""
        try:
            data = json.loads(request.body)
            actor = get_object_or_404(Actor, user__username=username)
            Activity.objects.create(
                actor=actor,
                object_data=data,
                activity_type=data.get('type'),
            )
            return JsonResponse({'status': 'accepted'}, status=202)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    def get_activity(self, _, username):
        """Returns the ActivityPub representation of an Actor's outbox."""
        actor = get_object_or_404(Actor, user__username=username)
        activities = Activity.objects.filter(
            actor=actor).order_by('-published_at')

        return JsonResponse({
            '@context': 'https://www.w3.org/ns/activitystreams',
            'id': actor.outbox,
            'type': 'OrderedCollection',
            'totalItems': activities.count(),
            'orderedItems': [activity.object_data for activity in activities]
        })


class ObjectService:
    """Handles ActivityPub Object endpoints."""

    def get_object(self, _, object_id, as_activitypub=True):
        """Returns the ActivityPub representation of an Object for the given ID."""
        obj = get_object_or_404(Object, id=object_id)
        if as_activitypub:
            return JsonResponse(obj.as_activitypub())
        return JsonResponse({
            'id': obj.id,
            'actor': obj.actor.user.username,
            'object_type': obj.object_type,
            'content': obj.content,
            'created_at': obj.created_at,
            'updated_at': obj.updated_at,
        })

    def create_object(self, request, username):
        """Creates a new Object from the given data."""
        try:
            data = json.loads(request.body)
            actor = get_object_or_404(Actor, user__username=username)
            obj = Object.objects.create(
                actor=actor,
                object_type=data.get('type'),
                content=data.get('content'),
            )
            return JsonResponse(obj.as_activitypub())
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)


class VaultService:
    """Handles Vault endpoints."""

    @staticmethod
    def get_private_key(username):
        """Fetches the private key for an actor securely"""
        vault = Vault.objects.filter(actor__user__username=username).first()
        if not vault:
            raise PermissionDenied('Access denied: Private key not found.')
        return vault.private_key

    def authenticate(self, username, public_key):
        """Authenticates the user based on the public key."""
        try:
            actor = Actor.objects.get(user__username=username)
            vault = Vault.objects.get(actor=actor)
            stored_public_key = vault.private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode()

            if stored_public_key == public_key:
                return actor.user
            else:
                return None
        except (Actor.DoesNotExist, Vault.DoesNotExist):
            return None

    def check_user_vault(self, username):
        """Check if the vault already has the private key for the actor"""

        user = User.objects.filter(username=username).first()
        if not user:
            return JsonResponse({'error': 'User not found'}, status=404)

        vault = Vault.objects.filter(actor__user__username=username).first()
        if not vault:
            return JsonResponse({'error': 'Private key not found in vault'}, status=404)

        return JsonResponse({'message': 'Vault already has the private key'})


class AuthenticationService:
    """
    Handles authentication for the socialize app
    using OAuth providers like Google and Facebook
    """

    def authenticate(self, request, user_data, access_token):
        """Authenticate the user using the OAuth provider."""

        # If OAuth authentication is not successful, create the actor
        user = authenticate(username=user_data['username'])
        if not user:
            user = ActorService().create_actor(
                {'username': user_data['username']}).user

        login(request, user)

        # If OAuth login process is successful, return the access token
        token, _ = Token.objects.get_or_create(
            access_token=access_token, user=user)
        return JsonResponse({'access_token': token.access_token, 'expires_in': 3600})

    def verify_access_token(self, provider, token):
        """Check if key is in AccessToken key and not expired."""
        provider_urls = {
            'google': 'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={token}',
            'facebook': 'https://graph.facebook.com/me?access_token={token}&fields=email',
        }

        if provider not in provider_urls:
            return None

        response = requests.get(
            provider_urls[provider].format(token=token), timeout=10)
        if response.status_code != 200:
            return None

        return response.json()
