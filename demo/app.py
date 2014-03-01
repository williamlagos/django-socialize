import re
from unicodedata import normalize
from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse as response
from django.http import HttpResponseRedirect as redirect
from django.conf import settings

from demo.models import Spreadable,Image,Playable,Spreaded
from socialize.models import Profile
from socialize.stream import StreamService,Dropbox
from main import Efforia

def sp(x): return '!!' in x[1]
def pl(x): return '>!' in x[1]
def im(x): return '%!' in x[1]
        
class Images(Efforia):
    def __init__(self): pass
    def view_image(self,request):
        return render(request,'image.jade',{'static_url':settings.STATIC_URL},content_type='text/html')
    def upload_image(self,request):
        photo = request.FILES['Filedata'].read()
        dropbox = Dropbox()
        link = dropbox.upload_and_share(photo)
        res = self.url_request(link)
        url = '%s?dl=1' % res
        return url
    def create_image(self,request):
        u = self.current_user(request)
        if 'description' in request.POST:
            image = list(Image.objects.filter(user=u))[-1:][0]
            descr = request.POST['description']
            image.description = descr
            image.save()
            return response('Description added to image successfully')
        i = Image(link=self.upload_image(request),user=u)
        i.save()
        return response('Image created successfully')

class Spreads(Efforia):
    def __init__(self): pass
    def start_spreadapp(self,request):
        return render(request,'spreadapp.jade',{'static_url':settings.STATIC_URL},content_type='text/html')
    def view_spread(self,request):
        return render(request,"spread.jade",{},content_type='text/html')
    def create_spread(self,request):
        u = self.current_user(request)
        name = u.first_name.lower()
        text = unicode('%s' % (request.POST['content']))
        post = Spreadable(user=u,content=text,name='!'+name)
        post.save()
        self.accumulate_points(1,request)
        return response('Spreadable created successfully')
    
class Uploads(Efforia):
    def __init__(self): pass
    def view_upload(self,request):
        return render(request,'content.jade',{'static_url':settings.STATIC_URL},content_type='text/html')
    def set_thumbnail(self,request):
        u = self.current_user(request)
        service = StreamService()
        token = request.GET['id']
        access_token = u.profile.google_token
        thumbnail = service.video_thumbnail(token,access_token)
        play = Playable.objects.filter(user=u).latest('date')
        play.visual = thumbnail
        play.token = token
        play.save()
        self.accumulate_points(1,request)
        r = redirect('/')
        r.set_cookie('token',token)
        return r
    def view_content(self,request):
        u = self.current_user(request)
        content = title = ''
        for k,v in request.REQUEST.iteritems(): 
            if 'title' in k: title = v
            elif 'content' in k: content = v
            elif 'status' in k: 
                return self.set_thumbnail(request)
        try: 
            url,token = self.parse_upload(request,title,content)
            return render(request,'video.jade',{'static_url':settings.STATIC_URL,
                                                  'hostname':request.get_host(),
                                                  'url':url,'token':token},content_type='text/html')
        except Exception: return response('Invalid file for uploading') 
    def parse_upload(self,request,title,content):
        keys = ','; keywords = content.split(' ')
        for k in keywords: k = normalize('NFKD',k.decode('utf-8')).encode('ASCII','ignore')
        keys = keys.join(keywords)
        playable = Playable(user=self.current_user(request),name='>'+title,description=content)
        playable.save()
        service = StreamService()
        access_token = self.current_user(request).profile.google_token
        return service.video_entry(title,content,keys,access_token)
    def media_chooser(self,request):
        return render(request,'chooser.jade')
