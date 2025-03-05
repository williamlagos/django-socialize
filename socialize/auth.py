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

import logging


class OAuthError(RuntimeError):
    """Generic exception class."""

    def __init__(self, message='OAuth error occured.'):
        self.message = message


class OAuth20Authentication(Authentication):
    """
    OAuth authenticator. 

    This Authentication method checks for a provided HTTP_AUTHORIZATION
    and looks up to see if this is a valid OAuth Access Token
    """

    def __init__(self, realm='API'):
        self.realm = realm

    def is_authenticated(self, request, **kwargs):
        """
        Verify 2-legged oauth request. Parameters accepted as
        values in "Authorization" header, or as a GET request
        or in a POST body.
        """
        logging.info("OAuth20Authentication")

        try:
            key = request.GET.get('oauth_consumer_key')
            if not key:
                key = request.POST.get('oauth_consumer_key')
            if not key:
                auth_header_value = request.META.get('HTTP_AUTHORIZATION')
                if auth_header_value:
                    key = auth_header_value.split(' ')[1]
            if not key:
                logging.error('OAuth20Authentication. No consumer_key found.')
                return None
            """
            If verify_access_token() does not pass, it will raise an error
            """
            token = verify_access_token(key)

            # If OAuth authentication is successful, set the request user to the token user for authorization
            request.user = token.user

            # If OAuth authentication is successful, set oauth_consumer_key on request in case we need it later
            request.META['oauth_consumer_key'] = key
            return True
        except KeyError as e:
            logging.exception("Error in OAuth20Authentication.")
            request.user = AnonymousUser()
            return False
        except Exception as e:
            logging.exception("Error in OAuth20Authentication.")
            return False
        return True


def verify_access_token(key):
    # Check if key is in AccessToken key
    try:
        token = AccessToken.objects.get(token=key)

        # Check if token has expired
        if token.expires < timezone.now():
            raise OAuthError('AccessToken has expired.')
    except AccessToken.DoesNotExist as e:
        raise OAuthError("AccessToken not found at all.")

    logging.info('Valid access')
    return token
