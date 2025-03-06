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

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.conf import settings

from .models import Actor, Activity, Object, Vault


class ActorService:
    """Handles ActivityPub Actor endpoints."""

    def get(self, request, *_, **kwargs):
        """Handles GET requests for actor-related actions."""
        route = kwargs.get('route')

        if route == 'actor':
            return self.get_actor(request, kwargs.get('username'))
        elif route == 'webfinger':
            return self.get_webfinger(request)

        return JsonResponse({'error': 'Invalid endpoint'}, status=404)

    @method_decorator(csrf_exempt, name='dispatch')
    def post(self, request):
        """Handles POST requests for actor-related actions."""
        data = json.loads(request.body)
        username = data.get('username')

        if not username:
            return JsonResponse({'error': 'Username is required'}, status=400)

        actor = self.create_actor(data)
        return JsonResponse({'id': actor.get_actor_url()}, status=201)

    def get_actor(self, _, username):
        """Returns the ActivityPub representation of an Actor for the given username."""
        actor = get_object_or_404(Actor, username=username)
        return JsonResponse(actor.as_activitypub())

    def create_actor(self, data):
        """Creates a new Actor from the given data."""
        private_key, public_key = self.generate_keys()

        actor = Actor.objects.create(
            username=data.get('username'), public_key=public_key)
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
            actor = get_object_or_404(Actor, username=username)

            return JsonResponse({
                'subject': f'acct:{actor.username}@{settings.SITE_DOMAIN}',
                'links': [{
                    'rel': 'self',
                    'type': 'application/activity+json',
                    'href': actor.get_actor_url()
                }]
            })

        return JsonResponse({'error': 'Invalid WebFinger request'}, status=400)

    # TODO: Consider merging the logic in the old profiles class code methods below into the ActorService class.
    def accumulate_points(self, points, request=None):
        if request is None:
            u = self.current_user()
        else:
            u = self.current_user(request)
        current_profile = Profile.objects.all().filter(user=u)[0]
        current_profile.points += points
        current_profile.save()

    def update_profile(self, request, url, user):
        birthday = career = bio = ''
        p = user.profile
        for k, v in request.POST.items():
            if 'birth' in k:
                p.birthday = self.convert_datetime(v)
            elif 'career' in k:
                p.career = v
            elif 'bio' in k:
                p.bio = v
        p.save()
        return HttpResponse('Added informations to profile successfully')
