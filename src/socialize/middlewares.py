"""Middlewares for the social network."""
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

import base64
import logging

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.exceptions import InvalidSignature

from django.http import JsonResponse

from .models import Actor
from .services import VaultService


class ActivityPubSigningMiddleware:
    """Middleware to handle signing and verifying ActivityPub requests."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process incoming request
        if request.method in ['POST', 'PUT', 'PATCH']:
            if not self.verify_request(request):
                return JsonResponse({'error': 'Invalid signature'}, status=400)

        response = self.get_response(request)

        # Process outgoing response
        if request.method in ['POST', 'PUT', 'PATCH']:
            self.sign_response(request, response)

        return response

    def sign_response(self, request, response):
        """Signs an outgoing response using the Actor's private key."""
        username = request.user.username
        data = response.content.decode()
        signature = self.sign_request(username, data)
        response['Signature'] = signature

    def sign_request(self, username, data):
        """Signs an outgoing request using the Actor's private key."""
        private_key_pem = VaultService.get_private_key(username)
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode(), password=None
        )
        signature = private_key.sign(data.encode(), padding.PKCS1v15(), SHA256())

        return base64.b64encode(signature).decode()

    def verify_request(self, request):
        """Verifies an incoming request using the Actor's public key."""
        username = request.META.get('HTTP_USERNAME')
        received_signature = request.META.get('HTTP_SIGNATURE')
        data = request.body.decode()

        if not username or not received_signature:
            return False

        actor = Actor.objects.get(username=username)
        if not actor:
            return False

        public_key_pem = actor.public_key
        public_key = serialization.load_pem_public_key(public_key_pem.encode())

        decoded_signature = base64.b64decode(received_signature)

        try:
            public_key.verify(
                decoded_signature, data.encode(), padding.PKCS1v15(), SHA256()
            )
            return True
        except (InvalidSignature, ValueError):
            logging.exception('Error verifying signature.')
            return False
