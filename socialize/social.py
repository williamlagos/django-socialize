#
# This file is part of Efforia Open Source Initiative.
#
# Copyright (C) 2011-2013 William Oliveira de Lagos <william@Socialize.com.br>
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
#!/usr/bin/python
# -*- coding: utf-8 -*-

import json,urllib,urllib2,re,logging,oauth2 as oauth
from datetime import datetime
from time import mktime,strptime

from django.http import HttpResponse as response
from django.http import HttpResponseRedirect as redirect
from django.shortcuts import render
from django.db import IntegrityError
from django.contrib.auth.models import AnonymousUser, User
#from tastypie.authentication import Authentication
#from provider.oauth2.models import AccessToken

from models import *
from forms import TutorialForm
from core import Socialize

class Search(Socialize):
    def __init__(self): pass
    def explore(self,request):
        try: query = request.GET['explore']
        except KeyError,e: query = ''
        u = self.current_user(request)
        others = [x['id'] for x in Profile.objects.values('id')]
        objects = self.feed(u,others)
        filter(lambda obj: query.lower() in obj.name.lower(),objects)  
        return self.view_mosaic(request,objects) 

class Follows(Socialize):
    def __init__(self): pass
    def view_following(self,request):
        u = self.current_user(request); rels = []
        for f in Followed.objects.filter(follower=u.id):
            rels.append(Profile.objects.filter(user_id=f.followed)[0])
        request.COOKIES['permissions'] = 'view_only'
        return self.view_mosaic(request,rels)
    def become_follower(self,request):
        u = self.current_user(request).id
        followed = Profile.objects.filter(id=request.GET['profile_id'])[0].user_id
        follow = Followed(followed=followed,follower=u)
        follow.save()
        return response('Profile followed successfully')
    def leave_follower(self,request):
        u = self.current_user(request).id
        followed = request.GET['profile_id']
        query = Followed.objects.filter(followed=followed,follower=u)
        if len(query): query[0].delete()
        return response('Profile unfollowed successfully')


class ID(Socialize):
    def __init__(self): pass
    def view_id(self,request):
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
    def finish_tutorial(self,request):
        u = self.current_user(request)
        p = Profile.objects.all().filter(user=u)[0]
        p.first_time = False
        p.save()
        return response('Tutorial finalizado.')        

class Deletes(Socialize):
    def delete_element(self,request):
        oid = request.GET['id']
        modobj = settings.Socialize_TOKENS[request.GET['token']]
        module,obj = modobj.split('.')
        o = self.class_module('%s.models'%module,obj)
        query = o.objects.filter(id=oid)
        if len(query): query[0].delete()
        return response('Object deleted successfully')
    
class Tutorial(Socialize):
    def view_tutorial(self,request):
        social = False if 'social' not in request.GET else True
        form = TutorialForm()
        return render(request,'tutorial.html',{'form':form,'static_url':settings.STATIC_URL,'social':social})
    def update_profile(self,request,url,user):
        birthday = career = bio = ''
        p = user.profile
        for k,v in request.POST.iteritems():
            if 'birth' in k: p.birthday = self.convert_datetime(v)
            elif 'career' in k: p.career = v
            elif 'bio' in k: p.bio = v
        p.save()
        return response('Added informations to profile successfully')
    def finish_tutorial(self,request):
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
    
class Authentication(Socialize):
    def social_update(self,request,typesoc,profile):
        data = request.REQUEST
        u = self.current_user(request)
        p = Profile.objects.filter(user=u)[0]
        if 'google' in typesoc: p.google_token = profile['google_token'] 
        elif 'twitter' in typesoc: p.twitter_token = '%s;%s' % (profile['key'],profile['secret'])
        elif 'facebook' in typesoc: p.facebook_token = profile['facebook_token']
        p.save()       
        return redirect('/')
    def social_register(self,request,typesoc,profile):
        data = request.REQUEST
        whitespace = ' '; r = None;
        facebook = twitter = google = ''
        if 'google' in typesoc:
            username = profile['name'].lower()
            google = profile['google_token']
        elif 'twitter' in typesoc:
            username = profile['screen_name']
            twitter = '%s;%s' % (profile['key'],profile['secret'])
        elif 'facebook' in typesoc:
            username = profile['link'].split('/')[-1:][0]
            facebook = profile['facebook_token']
        # Ja registrado, fazer login social
        if len(list(User.objects.filter(username=username))) > 0:
            request.session['user'] = username
            r = redirect('/')
        # Nao registrado, gravando chaves sociais e perfil e redirecionando para tutorial
        else: 
            u = User.objects.create_user(username,password=User.objects.make_random_password())
            p = Profile(user=u,facebook_token=facebook,twitter_token=twitter,google_token=google)
            p.save()
            r = redirect('tutorial?social=%s'%data['social'])
            r.set_cookie('username',username)
        r.set_cookie('permissions','super')
        return r
    def authenticate(self,request):
        data = request.REQUEST
        if 'profile' in data:
            profile = self.json_decode(data['profile']); t = data['social']
            # Atualizacao do perfil com tokens sociais
            if 'user' in request.session: return self.social_update(request,t,profile)
            # Registro do perfil com token social
            else: return self.social_register(request,t,profile)
        elif 'username' not in data or 'password' not in data:
            return response(json.dumps({'error':'User or password missing'}),mimetype='application/json')
        else:
            username = data['username']
            password = data['password']
            exists = User.objects.filter(username=username)
            if exists:
                if exists[0].check_password(password):
                    obj = json.dumps({'username':username,'userid':exists[0].id})
                    request.session['user'] = username
                    r = response(json.dumps({'success':'Login successful'}),
                                    mimetype = 'application/json')
                    r.set_cookie('permissions','super')
                    return r
                else:
                    obj = json.dumps({'error':'User or password wrong'})
                    return response(obj,mimetype='application/json')
            else:
                obj = json.dumps({'error':'User does not exist'})
                return response(obj,mimetype='application/json')
    def leave(self,request):
        del request.session['user']
        return response(json.dumps({'success':'Logout successful'}),mimetype='application/json')
    def view_register(self,request):
        return render(request,'register.html',{'static_url':settings.STATIC_URL,'hostname':request.get_host()},content_type='text/html')
    def participate(self,request):
        whitespace = ' '
        username = password = first_name = last_name = ''
        for k,v in request.POST.iteritems():
            if 'username' in k:
                u = User.objects.filter(username=v)
                if len(u) > 0: return response('Username already exists')
                else: username = v
            elif 'password' in k:
                if v not in request.POST['repeatpassword']: return response('Password mismatch')
                else: password = v
            elif 'name' in k: first_name,last_name = whitespace.join(v.split()[:1]),whitespace.join(v.split()[1:])
        user = User(username=username,first_name=first_name,last_name=last_name)
        user.set_password(password)
        user.save()
        r = redirect('/Socialize/tutorial')
        r.set_cookie('username',username)
        r.set_cookie('permissions','super')
        return r

class Twitter(Socialize):
    def update_status(self,request):
        u = self.current_user(request)
        if len(request.GET['content']) > 137: 
            short = unicode('%s...' % (request.GET['content'][:137]))
        else: short = unicode('%s' % (request.GET['content']))
        tokens = u.profile.twitter_token
        if not tokens: tokens = self.own_access()['twitter_token']
        data = {'status':short.encode('utf-8')}
        self.oauth_post_request('/statuses/update.json',tokens,data,'twitter')
        return response('Published posting successfully on Twitter')

class Facebook(Socialize):
    def update_status(self,request):
        u = self.current_user(request)
        token = u.profile.facebook_token
        text = unicode('%s' % request.GET['content'])
        data = {'message':text.encode('utf-8')}
        if 'id' in request.REQUEST: url = '/%s/feed' % request.REQUEST['id']
        else: url = '/me/feed'
        self.oauth_post_request(url,token,data,'facebook')
        return response('Published posting successfully on Facebook')
    def send_event(self,request):
        u = self.current_user(request)
        token = u.profile.facebook_token
        name = dates = descr = local = value = '' 
        for k,v in request.REQUEST.iteritems():
            if 'name' in k: name = v.encode('utf-8')
            elif 'deadline' in k: dates = v
            elif 'description' in k: descr = v.encode('utf-8')
            elif 'location' in k: local = v.encode('utf-8')
            elif 'value' in k: value = v
        date = self.convert_datetime(dates)
        url = 'http://%s/Socialize/basket?alt=redir&id=%s&value=%s&token=@@'%(settings.Socialize_URL,value,name)
        data = {'name':name,'start_time':date,'description':descr,'location':local,'ticket_uri':url}
        id = json.loads(self.oauth_post_request("/me/events",token,data,'facebook'))['id']
        return response(id)
    def send_event_cover(self,request):
        u = self.current_user(request)
        token = u.profile.facebook_token
        ident = request.REQUEST['id']
        photo = request.REQUEST['url']
        self.oauth_post_request('/%s'%ident,token,{'cover_url':photo},'facebook')
        return response('Published image cover on event successfully on Facebook')

class Coins(Socialize):
    def discharge(self,request):
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
    def recharge(self,request):
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
    def balance(self,request):
        userid = request.GET['userid']
        json.dumps({'objects':{
            'userid': userid,
            'value': Profile.objects.filter(user=int(userid))[0].credit
        }})
        return response(j,mimetype='application/json')

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
        except KeyError, e:
            logging.exception("Error in OAuth20Authentication.")
            request.user = AnonymousUser()
            return False
        except Exception, e:
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
    except AccessToken.DoesNotExist, e:
        raise OAuthError("AccessToken not found at all.")

    logging.info('Valid access')
    return token
