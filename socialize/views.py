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
import urllib
import ast
import time

from datetime import datetime
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponse
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, render
from django.conf import settings
from django.urls import path

from .models import Actor, Activity, Object, Vault


class ActorService(View):
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

    @staticmethod
    def get_urlpatterns():
        """Returns the URL patterns for the ActorService."""
        return [
            path('users/<str:username>/', ActorService.as_view(),
                 {'route': 'actor'}, name='actor'),
            path('.well-known/webfinger', ActorService.as_view(),
                 {'route': 'webfinger'}, name='webfinger'),
        ]

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


class ActivityService(View):
    """Handles ActivityPub Activity endpoints for inbox and outbox."""

    def get(self, request, *_, **kwargs):
        """Handles GET requests for activity-related actions."""
        route = kwargs.get('route')

        if route == 'outbox':
            return self.get_outbox(request, kwargs.get('username'))

        return JsonResponse({'error': 'Invalid endpoint'}, status=404)

    @method_decorator(csrf_exempt)
    def post(self, request, *_, **kwargs):
        """Handles POST requests for activity-related actions on inbox."""
        route = kwargs.get('route')

        if route == 'inbox':
            return self.post_inbox(request, kwargs.get('username'))

        return HttpResponseNotAllowed(['POST'])

    def post_inbox(self, request, username):
        """Handles ActivityPub inbox messages."""
        try:
            data = json.loads(request.body)
            actor = get_object_or_404(Actor, username=username)
            Activity.objects.create(
                actor=actor,
                object_data=data,
                activity_type=data.get('type'),
            )
            return JsonResponse({'status': 'accepted'}, status=202)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    def get_outbox(self, _, username):
        """Returns the ActivityPub representation of an Actor's outbox."""
        actor = get_object_or_404(Actor, username=username)
        activities = Activity.objects.filter(
            actor=actor).order_by('-published_at')

        return JsonResponse({
            '@context': 'https://www.w3.org/ns/activitystreams',
            'id': actor.outbox,
            'type': 'OrderedCollection',
            'totalItems': activities.count(),
            'orderedItems': [activity.object_data for activity in activities]
        })

    @staticmethod
    def get_urlpatterns():
        """Returns the URL patterns for the ActivityService."""
        return [
            path('users/<str:username>/outbox/', ActivityService.as_view(),
                 {'route': 'outbox'}, name='outbox'),
            path('users/<str:username>/inbox/', ActivityService.as_view(),
                 {'route': 'inbox'}, name='inbox'),
        ]

    # TODO: Consider merging the logic in the following class code methods below into the ActivityService class.
    def view_following(self, request):
        u = self.current_user(request)
        rels = []
        for f in Followed.objects.filter(follower=u.id):
            rels.append(Profile.objects.filter(user_id=f.followed)[0])
        request.COOKIES['permissions'] = 'view_only'
        return self.view_mosaic(request, rels)

    def become_follower(self, request):
        u = self.current_user(request).id
        followed = Profile.objects.filter(
            id=request.GET['profile_id'])[0].user_id
        follow = Followed(followed=followed, follower=u)
        follow.save()
        return HttpResponse('Profile followed successfully')

    def leave_follower(self, request):
        u = self.current_user(request).id
        followed = request.GET['profile_id']
        query = Followed.objects.filter(followed=followed, follower=u)
        if len(query):
            query[0].delete()
        return HttpResponse('Profile unfollowed successfully')


class ObjectService(View):
    """Handles ActivityPub Object endpoints."""

    def get(self, request, *_, **kwargs):
        """Handles GET requests for object-related actions."""
        route = kwargs.get('route')

        if route == 'object':
            return self.get_object(request, kwargs.get('object_id'))

        return JsonResponse({'error': 'Invalid endpoint'}, status=404)

    def get_object(self, _, object_id):
        """Returns the ActivityPub representation of an Object for the given ID."""
        obj = get_object_or_404(Object, id=object_id)
        return JsonResponse(obj.as_activitypub())

    @staticmethod
    def get_urlpatterns():
        """Returns the URL patterns for the ObjectService."""
        return [
            path('objects/<uuid:object_id>/', ObjectService.as_view(),
                 {'route': 'object'}, name='object'),
        ]

    # TODO: Consider mergint the logic in the Search and Delete class code methods below with the ObjectService class.
    def delete_element(self, request):
        oid = request.GET['id']
        modobj = settings.Socialize_TOKENS[request.GET['token']]
        module, obj = modobj.split('.')
        o = self.class_module('%s.models' % module, obj)
        query = o.objects.filter(id=oid)
        if len(query):
            query[0].delete()
        return HttpResponse('Object deleted successfully')

    def explore(self, request):
        try:
            query = request.GET['explore']
        except KeyError as e:
            query = ''
        u = self.current_user(request)
        others = [x['id'] for x in Profile.objects.values('id')]
        objects = self.feed(u, others)
        [obj for obj in objects if query.lower() in obj.name.lower()]
        return self.view_mosaic(request, objects)


class VaultService(View):
    """Handles Vault endpoints."""

    @staticmethod
    def get_private_key(username):
        """Fetches the private key for an actor securely"""
        vault = Vault.objects.filter(actor__username=username).first()
        if not vault:
            raise PermissionDenied('Access denied: Private key not found.')
        return vault.private_key

    # TODO: Consider revamping these authentication methods into a new VaultService class
    def object_byid(self, token, ident):
        obj = self.object_token(token)
        return globals()[obj].objects.filter(id=ident)[0]

    def authenticate(self, username, password):
        exists = User.objects.filter(username=username)
        if exists:
            if exists[0].check_password(password):
                return exists
        else:
            return None

    def authenticated(self):
        name = self.get_current_user()
        if not name:
            # self.redirect('login')
            self.render('templates/enter.html', STATIC_URL=settings.STATIC_URL)
            return False
        else:
            return True

    def view_id(self, request):
        u = self.current_user(request)
        if 'first_turn' in request.GET:
            if u.profile.first_turn:
                return HttpResponse('yes')
            else:
                return HttpResponse('no')
        elif 'object' in request.GET:
            o, t = request.GET['object'][0].split(';')
            now, objs, rels = self.get_object_bydate(o, t)
            obj = globals()[objs].objects.all().filter(date=now)[0]
            if hasattr(obj, 'user'):
                return HttpResponse(str(obj.user.id))
            else:
                return HttpResponse(str(self.current_user().id))
        else:
            return HttpResponse(str(self.current_user().id))

    def is_tutorial_finished(self, request):
        u = self.current_user(request)
        p = Profile.objects.all().filter(user=u)[0]
        p.first_time = False
        p.save()
        return HttpResponse('Tutorial finalizado.')

    def view_tutorial(self, request):
        social = False if 'social' not in request.GET else True
        return render(request, 'tutorial.html', {
            'static_url': settings.STATIC_URL,
            'social': social
        })

    def finish_tutorial(self, request):
        whitespace = ' '
        data = request.POST
        name = request.COOKIES['username']
        u = User.objects.filter(username=name)[0]
        if 'name' in data:
            lname = data['name'].split()
            u.first_name, u.last_name = lname[0], whitespace.join(lname[1:])
        u.save()
        request.session['user'] = name
        if len(request.POST) is 0:
            # return redirect('/')
            return HttpResponse('Added informations to profile successfully')
        else:
            return self.update_profile(request, '/', u)

    def profile_render(self, _):
        source = """
            <div class="col-xs-12 col-sm-6 col-md-3 col-lg-2 brick">
                <a class="block profile" href="#" style="display:block; background:black">
                <div class="box profile">
                <div class="content">
                <h2 class="name">{{ firstname }}</h2>
                <div class="centered">{{ career }}</div>
                </div>
                {% if visual %}
                    <img src="{{ visual }}" width="100%"/>
                {% else %}
                    <h1 class="centered"><span class="glyphicon glyphicon-user big-glyphicon"></span></h1>
                {% endif %}
                <div class="content centered">
                {{ bio }}
                <div class="id hidden">{{ id }}</div></div></div>
                <div class="date"> Entrou em {{ day }} de {{month}}</div>
            </a></div>
        """
        return Template(source).render(Context({
            'firstname': self.user.first_name,
            'career':    self.career,
            'id':        self.id,
            'visual':    self.visual,
            'bio':       self.bio,
            'day':       self.date.day,
            'month':     self.month
        }))

    def verify_permissions(self, request):
        perm = 'super'
        if 'permissions' in request.COOKIES:
            perm = request.COOKIES['permissions']
        permissions = True if 'super' in perm else False
        return permissions

    def start(self, request):
        # Painel do usuario
        # u = user('efforia');
        # permissions = self.verify_permissions(request)
        # actions = settings.EFFORIA_ACTIONS; apps = []
        # for a in settings.EFFORIA_APPS: apps.append(actions[a])
        # return render(request,'interface.html',{'static_url':settings.STATIC_URL,
        #                                     'user':user('efforia'),'perm':permissions,
        #                                     'name':'%s %s' % (u.first_name,u.last_name),'apps':apps
        #                                     },content_type='text/html')
        # Pagina inicial
        return render(request, 'index.html', {'static_url': settings.STATIC_URL}, content_type='text/html')

    # TODO: Consider moving this whole coins class code to another package.
    def external(self, request):
        u = self.current_user(request)
        sellables = Sellable.objects.filter(user=u)
        for s in sellables:
            s.paid = True
        return self.redirect('/')

    def discharge(self, request):
        userid = request.REQUEST['userid']
        values = request.REQUEST['value']
        u = Profile.objects.filter(user=(userid))[0]
        u.credit -= int(values)
        u.save()
        j = json.dumps({'objects': {
            'userid': userid,
            'value': u.credit
        }})
        return HttpResponse(j, mimetype='application/json')

    def recharge(self, request):
        userid = request.REQUEST['userid']
        values = request.REQUEST['value']
        u = Profile.objects.filter(user=(userid))[0]
        u.credit += int(values)
        u.save()
        json.dumps({'objects': {
            'userid': userid,
            'value': u.credit
        }})
        return HttpResponse(j, mimetype='application/json')

    def balance(self, request):
        userid = request.GET['userid']
        json.dumps({'objects': {
            'userid': userid,
            'value': Profile.objects.filter(user=int(userid))[0].credit
        }})
        return HttpResponse(j, mimetype='application/json')


def user(name):
    """Return a User object by username."""
    return User.objects.filter(username=name)[0]


def superuser():
    """Return the first superuser."""
    return User.objects.filter(is_superuser=True)[0]


def convert_datetime(date_value):
    """Converts a date string to a datetime object."""
    d = time.strptime(date_value, '%d/%m/%Y')
    return datetime.fromtimestamp(time.mktime(d))


def json_decode(string):
    """Decode a JSON string."""
    j = json.loads(string)
    return ast.literal_eval(j)


def url_request(url, data=None, headers=None):
    """Send a request"""
    request = urllib.request.Request(url=url, data=data, headers=headers)
    request_open = urllib.request.urlopen(request)
    return request_open.geturl()


def do_request(url, data=None, headers=None):
    """Do a request"""
    request = urllib.request.Request(url=url, data=data, headers=headers)
    try:
        request_open = urllib.request.urlopen(request)
        response = request_open.read()
        request_open.close()
    except urllib.error.HTTPError as e:
        print(url)
        print(data)
        print(headers)
        print(e.code)
        print(e.msg)
        print(e.hdrs)
        print(e.fp)
    return response
