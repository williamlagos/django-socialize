#
# This file is part of Efforia project.
#
# Copyright (C) 2011-2013 William Oliveira de Lagos <william@efforia.com.br>
#
# Efforia is free software: you can redistribute it and/or modify
# it under the terms of the Lesser GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Efforia is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Efforia. If not, see <http://www.gnu.org/licenses/>.
#
#!/usr/bin/python
# -*- coding: utf-8 -*-
from social import Search,Follows,ID,Deletes,Authentication,Twitter,Facebook,Tutorial,Coins

def discharge(request):
    c = Coins()
    if request.method == 'GET':
        c.discharge(request)

def recharge(request):
    c = Coins()
    if request.method == 'GET':
        c.recharge(request)

def balance(request):
    c = Coins()
    if request.method == 'GET':
        c.balance(request)

def payment(request):
    pay = Coins()
    if request.method == 'GET':
        return pay.view_recharge(request)
    elif request.method == 'POST':
        return pay.update_credit(request)

def search(request):
    s = Search()
    if request.method == 'GET':
        return s.explore(request)

def explore(request):
    p = Profiles()
    if request.method == 'GET':
        return p.view_userinfo(request)

def activity(request):
    p = Profiles()
    if request.method == 'GET':
        return p.view_activity(request)

def following(request):
    fav = Follows()
    if request.method == 'GET':
        return fav.view_following(request)

def follow(request):
    f = Follows()
    if request.method == 'GET':
        return f.become_follower(request)

def unfollow(request):
    f = Follows()
    if request.method == 'GET':
        return f.leave_follower(request)

def ids(request):
    i = ID()
    if request.method == 'GET':
        return i.view_id(request)
    elif request.method == 'POST':
        return i.finish_tutorial(request)

def delete(request):
    d = Deletes()
    if request.method == 'GET':
        return d.delete_element(request)

def profile(request):
    prof = Profiles()
    if request.method == 'GET':
        return prof.view_profile(request)
    elif request.method == 'POST':
        return prof.update_profile(request)

def authenticate(request):
    a = Authentication()
    if request.method == 'GET':
        return a.authenticate(request)

def leave(request):
    a = Authentication()
    if request.method == 'GET':
        return a.leave(request)

def twitter_post(request):
    t = Twitter()
    if request.method == 'GET':
        return t.update_status(request)

def facebook_post(request):
    f = Facebook()
    if request.method == 'GET':
        return f.update_status(request)

def facebook_event(request):
    f = Facebook()
    if request.method == 'GET':
        return f.send_event(request)
    
def facebook_eventcover(request):
    f = Facebook()
    if request.method == 'GET':
        return f.send_event_cover(request)
    
def participate(request):
    a = Authentication()
    if request.method == 'GET':
        return a.view_register(request)
    elif request.method == 'POST':
        return a.participate(request)

def tutorial(request):
    t = Tutorial()
    if request.method == 'GET':
        return t.view_tutorial(request)
    elif request.method == 'POST':
        return t.finish_tutorial(request)