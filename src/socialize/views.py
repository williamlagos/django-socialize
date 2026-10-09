"""Views for the socialize app."""

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

import json

from django.http import HttpResponseNotAllowed, JsonResponse
from django.urls import path
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .services import (
    ActivityService,
    ActorService,
    AuthenticationService,
    ObjectService,
)


@method_decorator(csrf_exempt, name="dispatch")
class ActorView(View):
    """Handles ActivityPub Actor, WebFinger, Collections, and NodeInfo endpoints."""

    service = ActorService()

    def get(self, request, *_, **kwargs):
        """Handles GET requests for actor-related actions."""
        route = kwargs.get("route")

        if route == "actor":
            as_ap = (
                "activity_pub" in request.GET
                or "application/activity+json" in request.headers.get("Accept", "")
                or "application/ld+json" in request.headers.get("Accept", "")
                or True
            )
            return self.service.get_actor(
                request,
                kwargs.get("username"),
                as_activitypub=as_ap,
            )
        elif route == "webfinger":
            return self.service.get_webfinger(request)
        elif route == "followers":
            return self.service.get_followers(request, kwargs.get("username"))
        elif route == "following":
            return self.service.get_following(request, kwargs.get("username"))
        elif route == "nodeinfo_discovery":
            return self.service.get_nodeinfo_discovery(request)
        elif route == "nodeinfo_2_0":
            return self.service.get_nodeinfo_2_0(request)

        return JsonResponse({"error": "Invalid endpoint"}, status=404)

    def post(self, request, *_, **kwargs):
        """Handles POST requests for actor creation."""
        try:
            data = json.loads(request.body)
        except Exception:
            return JsonResponse({"error": "Invalid JSON body"}, status=400)

        username = data.get("username")
        if not username:
            return JsonResponse({"error": "Username is required"}, status=400)

        actor = self.service.create_actor(data)
        return JsonResponse({"id": actor.get_actor_url()}, status=201)

    @staticmethod
    def get_urlpatterns():
        """Returns the URL patterns for the ActorService."""
        return [
            path(
                "users/<str:username>/",
                ActorView.as_view(),
                {"route": "actor"},
                name="actor",
            ),
            path(
                "users/<str:username>/followers/",
                ActorView.as_view(),
                {"route": "followers"},
                name="followers",
            ),
            path(
                "users/<str:username>/following/",
                ActorView.as_view(),
                {"route": "following"},
                name="following",
            ),
            path(
                ".well-known/webfinger",
                ActorView.as_view(),
                {"route": "webfinger"},
                name="webfinger",
            ),
            path(
                ".well-known/nodeinfo",
                ActorView.as_view(),
                {"route": "nodeinfo_discovery"},
                name="nodeinfo_discovery",
            ),
            path(
                "nodeinfo/2.0",
                ActorView.as_view(),
                {"route": "nodeinfo_2_0"},
                name="nodeinfo_2_0",
            ),
        ]


@method_decorator(csrf_exempt, name="dispatch")
class ActivityView(View):
    """Handles ActivityPub Activity endpoints for inbox (personal & shared) and outbox."""

    service = ActivityService()

    def get(self, request, *_, **kwargs):
        """Handles GET requests for activity-related actions."""
        route = kwargs.get("route")

        if route == "outbox":
            return self.service.get_activity(request, kwargs.get("username"))

        return JsonResponse({"error": "Invalid endpoint"}, status=404)

    def post(self, request, *_, **kwargs):
        """Handles POST requests for activity-related actions on inbox."""
        route = kwargs.get("route")

        if route in ("inbox", "shared_inbox"):
            return self.service.create_activity(request, kwargs.get("username"))

        return HttpResponseNotAllowed(["POST"])

    @staticmethod
    def get_urlpatterns():
        """Returns the URL patterns for the ActivityService."""
        return [
            path(
                "users/<str:username>/outbox/",
                ActivityView.as_view(),
                {"route": "outbox"},
                name="outbox",
            ),
            path(
                "users/<str:username>/inbox/",
                ActivityView.as_view(),
                {"route": "inbox"},
                name="inbox",
            ),
            path(
                "inbox/",
                ActivityView.as_view(),
                {"route": "shared_inbox"},
                name="shared_inbox",
            ),
        ]


@method_decorator(csrf_exempt, name="dispatch")
class ObjectView(View):
    """Handles ActivityPub Object endpoints."""

    service = ObjectService()

    def get(self, request, *_, **kwargs):
        """Handles GET requests for object-related actions."""
        route = kwargs.get("route")

        if route == "object":
            return self.service.get_object(
                request,
                kwargs.get("object_id"),
                as_activitypub=True,
            )

        return JsonResponse({"error": "Invalid endpoint"}, status=404)

    def post(self, request, *_, **kwargs):
        """Handles POST requests for object creation."""
        route = kwargs.get("route")

        if route == "object":
            return self.service.create_object(request, kwargs.get("username"))

        return HttpResponseNotAllowed(["POST"])

    @staticmethod
    def get_urlpatterns():
        """Returns the URL patterns for the ObjectService."""
        return [
            path("objects/", ObjectView.as_view(), {"route": "object"}, name="object"),
            path(
                "objects/<uuid:object_id>/",
                ObjectView.as_view(),
                {"route": "object"},
                name="object_detail",
            ),
        ]


@method_decorator(csrf_exempt, name="dispatch")
class AuthenticationView(View):
    """
    OAuth authenticator.
    Checks for a provided access token and authenticates with provider.
    """

    service = AuthenticationService()

    def post(self, request):
        """Verify 2-legged OAuth request."""
        provider = request.POST.get("provider")
        access_token = request.POST.get("access_token")

        if not provider or not access_token:
            return JsonResponse(
                {"error": "Missing provider or access_token"}, status=400
            )

        user_data = self.service.verify_access_token(provider, access_token)
        if not user_data:
            return JsonResponse({"error": "Invalid access_token"}, status=401)

        return self.service.authenticate(request, user_data, access_token)

    @staticmethod
    def get_urlpatterns():
        """Returns the URL patterns for the authentication service."""
        return [
            path("auth/", AuthenticationView.as_view(), name="auth"),
        ]
