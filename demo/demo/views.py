#!/usr/bin/python
# -*- coding: utf-8 -*-
from actions import Events,Projects,Movements,Promoteds
from socialize.core import Socialize,user

def main(request):
    e = Socialize()
    if request.method == 'GET':
        return e.start(request)

def project_form(request):
    proj = Projects()
    if request.method == 'GET':
        return proj.project_form(request)

def project(request,projectid):
    proj = Projects()
    if request.method == 'GET':
        return proj.view_project(request,projectid)

def eventid(request):
    event = Events()
    if request.method == 'GET':
        return event.event_id(request)

def enroll(request):
    event = Events()
    if request.method == 'GET':
        return event.show_enroll(request)

def promoted(request):
    prom = Promoteds()
    if request.method == 'GET':
        return prom.promoted(request)

def promote(request):
    prom = Promoteds()
    if request.method == 'GET':
        return prom.promote_form(request)
    elif request.method == 'POST':
        return prom.promote(request)

def movements(request):
    group = Movements()
    if request.method == 'GET':
        return group.movement_form(request)

def backers(request):
    proj = Projects()
    if request.method == 'GET':
        return proj.view_backers(request)

def event_image(request):
    e = Events()
    if request.method == 'POST':
        return e.event_image(request)

def eventview(request,eventid=1):
    e = Events()
    if request.method == 'GET':
        return e.view_event(request,eventid)

def event(request):
    graph = Events()
    if request.method == 'GET':
        return graph.event_form(request)
    elif request.method == 'POST':
        return graph.create_event(request)

def project_main(request):
    proj = Projects()
    if request.method == 'GET':
        return proj.project_form(request)
    elif request.method == 'POST':
        return proj.create_project(request)
    
def grab(request):
    proj = Projects()
    if request.method == 'GET':
        return proj.grab_project(request)

def pledge(request):
    proj = Projects()
    if request.method == 'GET':
        return proj.view_pledge(request)
    elif request.method == 'POST':
        return proj.pledge_project(request)

def link(request):
    proj = Projects()
    if request.method == 'GET':
        return proj.link_project(request)

def init_create(request):
    c = Projects()
    if request.method == 'GET':
        return c.start_promoteapp(request)

def movement(request):
    group = Movements()
    if request.method == 'GET':
        return group.view_movement(request)
    elif request.method == 'POST':
        return group.create_movement(request)
