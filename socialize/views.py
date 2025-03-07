"""Views for the socialize app."""
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

from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseNotAllowed
from django.utils.decorators import method_decorator
from django.urls import path

from .services import ActorService, ActivityService, ObjectService


class ActorView(View):
    """Handles ActivityPub Actor endpoints."""
    service = ActorService()

    def get(self, request, *_, **kwargs):
        """Handles GET requests for actor-related actions."""
        route = kwargs.get('route')

        if route == 'actor':
            return self.service.get_actor(request, kwargs.get('username'))
        elif route == 'webfinger':
            return self.service.get_webfinger(request)

        return JsonResponse({'error': 'Invalid endpoint'}, status=404)

    @method_decorator(csrf_exempt, name='dispatch')
    def post(self, request):
        """Handles POST requests for actor-related actions."""
        data = json.loads(request.body)
        username = data.get('username')

        if not username:
            return JsonResponse({'error': 'Username is required'}, status=400)

        actor = self.service.create_actor(data)
        return JsonResponse({'id': actor.get_actor_url()}, status=201)

    @staticmethod
    def get_urlpatterns():
        """Returns the URL patterns for the ActorService."""
        return [
            path('users/<str:username>/', ActorView.as_view(),
                 {'route': 'actor'}, name='actor'),
            path('.well-known/webfinger', ActorView.as_view(),
                 {'route': 'webfinger'}, name='webfinger'),
        ]


class ActivityView(View):
    """Handles ActivityPub Activity endpoints for inbox and outbox."""
    service = ActivityService()

    def get(self, request, *_, **kwargs):
        """Handles GET requests for activity-related actions."""
        route = kwargs.get('route')

        if route == 'outbox':
            return self.service.get_outbox(request, kwargs.get('username'))

        return JsonResponse({'error': 'Invalid endpoint'}, status=404)

    @method_decorator(csrf_exempt)
    def post(self, request, *_, **kwargs):
        """Handles POST requests for activity-related actions on inbox."""
        route = kwargs.get('route')

        if route == 'inbox':
            return self.service.post_inbox(request, kwargs.get('username'))

        return HttpResponseNotAllowed(['POST'])

    @staticmethod
    def get_urlpatterns():
        """Returns the URL patterns for the ActivityService."""
        return [
            path('users/<str:username>/outbox/', ActivityView.as_view(),
                 {'route': 'outbox'}, name='outbox'),
            path('users/<str:username>/inbox/', ActivityView.as_view(),
                 {'route': 'inbox'}, name='inbox'),
        ]


class ObjectView(View):
    """Handles ActivityPub Object endpoints."""
    service = ObjectService()

    def get(self, request, *_, **kwargs):
        """Handles GET requests for object-related actions."""
        route = kwargs.get('route')

        if route == 'object':
            return self.get_object(request, kwargs.get('object_id'))

        return JsonResponse({'error': 'Invalid endpoint'}, status=404)

    @staticmethod
    def get_urlpatterns():
        """Returns the URL patterns for the ObjectService."""
        return [
            path('objects/<uuid:object_id>/', ObjectService.as_view(),
                 {'route': 'object'}, name='object'),
        ]
