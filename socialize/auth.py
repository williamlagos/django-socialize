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

import json
import base64
import logging

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.exceptions import InvalidSignature

from django.http import HttpResponse as response
from django.http import HttpResponseRedirect as redirect
from django.contrib.auth.models import AnonymousUser, User

from .views import VaultService
from .models import Actor


class SignatureService:
    """Handles signing and verifying ActivityPub requests."""

    @staticmethod
    def sign_request(username, data):
        """Signs an outgoing request using the Actor's private key."""
        private_key_pem = VaultService.get_private_key(username)
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode(), password=None)
        signature = private_key.sign(
            data.encode(), padding.PKCS1v15(), SHA256())

        return base64.b64encode(signature).decode()

    @staticmethod
    def verify_request(username, received_signature, data):
        """Verifies an incoming request using the Actor's public key."""
        actor = Actor.objects.get(username=username)
        if not actor:
            return False

        public_key_pem = actor.public_key
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode())

        decoded_signature = base64.b64decode(received_signature)

        try:
            public_key.verify(decoded_signature, data.encode(),
                              padding.PKCS1v15(), SHA256())
            return True
        except (InvalidSignature, ValueError):
            logging.exception("Error verifying signature.")
            return False

    def social_update(self, request, typesoc, profile):
        data = request.REQUEST
        u = self.current_user(request)
        p = Profile.objects.filter(user=u)[0]
        if 'google' in typesoc:
            p.google_token = profile['google_token']
        elif 'twitter' in typesoc:
            p.twitter_token = '%s;%s' % (profile['key'], profile['secret'])
        elif 'facebook' in typesoc:
            p.facebook_token = profile['facebook_token']
        p.save()
        return redirect('/')

    def social_register(self, request, typesoc, profile):
        data = request.REQUEST
        whitespace = ' '
        r = None
        facebook = twitter = google = ''
        if 'google' in typesoc:
            username = profile['name'].lower()
            google = profile['google_token']
        elif 'twitter' in typesoc:
            username = profile['screen_name']
            twitter = '%s;%s' % (profile['key'], profile['secret'])
        elif 'facebook' in typesoc:
            username = profile['link'].split('/')[-1:][0]
            facebook = profile['facebook_token']
        # Ja registrado, fazer login social
        if len(list(User.objects.filter(username=username))) > 0:
            request.session['user'] = username
            r = redirect('/')
        # Nao registrado, gravando chaves sociais e perfil e redirecionando para tutorial
        else:
            u = User.objects.create_user(
                username, password=User.objects.make_random_password())
            p = Profile(user=u, facebook_token=facebook,
                        twitter_token=twitter, google_token=google)
            p.save()
            r = redirect('tutorial?social=%s' % data['social'])
            r.set_cookie('username', username)
        r.set_cookie('permissions', 'super')
        return r

    def authenticate(self, request):
        data = request.REQUEST
        if 'profile' in data:
            profile = self.json_decode(data['profile'])
            t = data['social']
            # Atualizacao do perfil com tokens sociais
            if 'user' in request.session:
                return self.social_update(request, t, profile)
            # Registro do perfil com token social
            else:
                return self.social_register(request, t, profile)
        elif 'username' not in data or 'password' not in data:
            return response(json.dumps({'error': 'User or password missing'}), mimetype='application/json')
        else:
            username = data['username']
            password = data['password']
            exists = User.objects.filter(username=username)
            if exists:
                if exists[0].check_password(password):
                    obj = json.dumps(
                        {'username': username, 'userid': exists[0].id})
                    request.session['user'] = username
                    r = response(json.dumps({'success': 'Login successful'}),
                                 mimetype='application/json')
                    r.set_cookie('permissions', 'super')
                    return r
                else:
                    obj = json.dumps({'error': 'User or password wrong'})
                    return response(obj, mimetype='application/json')
            else:
                obj = json.dumps({'error': 'User does not exist'})
                return response(obj, mimetype='application/json')

    def participate(self, request):
        whitespace = ' '
        username = password = first_name = last_name = ''
        for k, v in request.POST.items():
            if 'username' in k:
                u = User.objects.filter(username=v)
                if len(u) > 0:
                    return response('Username already exists')
                else:
                    username = v
            elif 'password' in k:
                if v not in request.POST['repeatpassword']:
                    return response('Password mismatch')
                else:
                    password = v
            elif 'name' in k:
                first_name, last_name = whitespace.join(
                    v.split()[:1]), whitespace.join(v.split()[1:])
        user = User(username=username, first_name=first_name,
                    last_name=last_name)
        user.set_password(password)
        user.save()
        r = redirect('/Socialize/tutorial')
        r.set_cookie('username', username)
        r.set_cookie('permissions', 'super')
        return r


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
