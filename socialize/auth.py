"""Authentication services for the social network."""
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

import requests

from django.views import View
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.urls import path

from .views import ActorService
from .models import Token


class AuthenticationService(View):
    """
    OAuth authenticator. 

    This Authentication method checks for a provided HTTP_AUTHORIZATION
    and looks up to see if this is a valid OAuth Access Token
    """

    def post(self, request):
        """
        Verify 2-legged oauth request. Parameters accepted as
        values in "Authorization" header, or as a GET request
        or in a POST body.
        """
        provider = request.POST.get(
            'provider')  # OAuth provider, e.g. 'google'
        access_token = request.POST.get(
            'access_token')  # Token from OAuth provider

        if not provider or not access_token:
            return JsonResponse({'error': 'Missing provider or access_token'}, status=400)

        # Verify token with the provider
        user_data = self.verify_access_token(provider, access_token)
        if not user_data:
            return JsonResponse({'error': 'Invalid access_token'}, status=401)

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

    @staticmethod
    def get_urlpatterns():
        """Returns the URL patterns for the authentication service."""
        return [
            path('auth/', AuthenticationService.as_view(), name='auth'),
        ]
