#!/usr/bin/python
#
# This file is part of django-socialize project.
#
# Copyright (C) 2011-2020 William Oliveira de Lagos <william.lagos@icloud.com>
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
import re
import logging

from datetime import datetime
from time import mktime,strptime

from django.http import HttpResponse as response
from django.http import HttpResponseRedirect as redirect
from django.shortcuts import render
from django.db import IntegrityError
from django.contrib.auth.models import AnonymousUser, User
from django.conf import settings
from django.shortcuts import render

# import oauth2 as oauth
#from tastypie.authentication import Authentication
#from provider.oauth2.models import AccessToken

from .models import *
from .forms import TutorialForm
from .core import Socialize

def user(name): return User.objects.filter(username=name)[0]
def superuser(): return User.objects.filter(is_superuser=True)[0]

class SocialService:

    def __init__(self): 
        pass

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
        return render(request,'index.html',{'static_url':settings.STATIC_URL},content_type='text/html')

    def external(self, request):
        u = self.current_user(request)
        sellables = Sellable.objects.filter(user=u)
        for s in sellables: s.paid = True
        return self.redirect('/')

    def profile_view(self, request, name):
        if len(list(User.objects.filter(username=name))) > 0: request.session['user'] = name
        r = redirect('/')
        r.set_cookie('permissions','view_only')
        return r

    def json_decode(self, string):
        j = json.loads(string,'utf-8')
        return ast.literal_eval(j)

    def url_request(self, url, data=None, headers={}):
        request = urllib.request.Request(url=url,data=data,headers=headers)
        request_open = urllib.request.urlopen(request)
        return request_open.geturl()

    def do_request(self, url, data=None, headers={}):
        response = ''
        request = urllib.request.Request(url=url,data=data,headers=headers)
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

    def object_token(self, token):
        relations = settings.EFFORIA_TOKENS
        typobject = relations[token]
        return typobject
    def object_byid(self,token, ident):
        obj = self.object_token(token)
        return globals()[obj].objects.filter(id=ident)[0]

    def convert_datetime(self, date_value):
        d = time.strptime(date_value,'%d/%m/%Y')
        return datetime.fromtimestamp(time.mktime(d))

    def authenticate(self, username, password):
        exists = User.objects.filter(username=username)
        if exists:
            if exists[0].check_password(password): 
                return exists
        else: return None

    def authenticated(self):
        name = self.get_current_user()
        if not name: 
            #self.redirect('login')
            self.render('templates/enter.html',STATIC_URL=settings.STATIC_URL)
            return False
        else:
            return True

    def accumulate_points(self, points, request=None):
        if request is None: u = self.current_user()
        else: u = self.current_user(request)
        current_profile = Profile.objects.all().filter(user=u)[0]
        current_profile.points += points
        current_profile.save()

    # Search class code
    
    def explore(self, request):
        try: query = request.GET['explore']
        except KeyError as e: query = ''
        u = self.current_user(request)
        others = [x['id'] for x in Profile.objects.values('id')]
        objects = self.feed(u,others)
        [obj for obj in objects if query.lower() in obj.name.lower()]  
        return self.view_mosaic(request,objects) 

    # Follows class code
    
    def view_following(self, request):
        u = self.current_user(request); rels = []
        for f in Followed.objects.filter(follower=u.id):
            rels.append(Profile.objects.filter(user_id=f.followed)[0])
        request.COOKIES['permissions'] = 'view_only'
        return self.view_mosaic(request,rels)

    def become_follower(self, request):
        u = self.current_user(request).id
        followed = Profile.objects.filter(id=request.GET['profile_id'])[0].user_id
        follow = Followed(followed=followed,follower=u)
        follow.save()
        return response('Profile followed successfully')

    def leave_follower(self, request):
        u = self.current_user(request).id
        followed = request.GET['profile_id']
        query = Followed.objects.filter(followed=followed,follower=u)
        if len(query): query[0].delete()
        return response('Profile unfollowed successfully')

    # ID class code
    
    def view_id(self, request):
        u = self.current_user(request)
        if 'first_turn' in request.GET:
            if u.profile.first_turn: return response('yes')
            else: return response('no')
        elif 'object' in request.GET:
            o,t = request.GET['object'][0].split(';')
            now,objs,rels = self.get_object_bydate(o,t)
            obj = globals()[objs].objects.all().filter(date=now)[0]
            if hasattr(obj,'user'): return response(str(obj.user.id))
            else: return response(str(self.current_user().id))
        else: return response(str(self.current_user().id))

    def finish_tutorial(self, request):
        u = self.current_user(request)
        p = Profile.objects.all().filter(user=u)[0]
        p.first_time = False
        p.save()
        return response('Tutorial finalizado.')        

    # Deletes class code

    def delete_element(self,request):
        oid = request.GET['id']
        modobj = settings.Socialize_TOKENS[request.GET['token']]
        module,obj = modobj.split('.')
        o = self.class_module('%s.models'%module,obj)
        query = o.objects.filter(id=oid)
        if len(query): query[0].delete()
        return response('Object deleted successfully')
    
    # Tutorial class code

    def view_tutorial(self, request):
        social = False if 'social' not in request.GET else True
        form = TutorialForm()
        return render(request,'tutorial.html',{'form':form,'static_url':settings.STATIC_URL,'social':social})

    def update_profile(self, request, url, user):
        birthday = career = bio = ''
        p = user.profile
        for k,v in request.POST.items():
            if 'birth' in k: p.birthday = self.convert_datetime(v)
            elif 'career' in k: p.career = v
            elif 'bio' in k: p.bio = v
        p.save()
        return response('Added informations to profile successfully')

    def finish_tutorial(self, request):
        whitespace = ' '
        data = request.POST
        name = request.COOKIES['username']
        u = User.objects.filter(username=name)[0]
        if 'name' in data: 
            lname = data['name'].split() 
            u.first_name,u.last_name = lname[0],whitespace.join(lname[1:])
        u.save()
        request.session['user'] = name
        if len(request.POST) is 0: return response('Added informations to profile successfully')#return redirect('/')
        else: return self.update_profile(request,'/',u)

    # Coins class code

    def discharge(self, request):
        userid = request.REQUEST['userid']
        values = request.REQUEST['value']
        u = Profile.objects.filter(user=(userid))[0]
        u.credit -= int(values)
        u.save()
        j = json.dumps({'objects':{
            'userid':userid,
            'value':u.credit
        }})
        return response(j,mimetype='application/json')

    def recharge(self, request):
        userid = request.REQUEST['userid']
        values = request.REQUEST['value']
        u = Profile.objects.filter(user=(userid))[0]
        u.credit += int(values)
        u.save()
        json.dumps({'objects':{
            'userid': userid,
            'value': u.credit
        }})
        return response(j,mimetype='application/json')

    def balance(self, request):
        userid = request.GET['userid']
        json.dumps({'objects':{
            'userid': userid,
            'value': Profile.objects.filter(user=int(userid))[0].credit
        }})
        return response(j,mimetype='application/json')
