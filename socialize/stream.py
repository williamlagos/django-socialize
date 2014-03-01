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

# ATTENTION: Deprecated module.


import json
from StringIO import StringIO
from xml.dom.minidom import parseString

try:
    import gdata.youtube
    import gdata.media
    from dropbox import client, rest, session
except ImportError,e:
    pass

#apis = json.load(open('settings.json','r'))
#google_api = apis['social']['google']
google_api = ('','')

class Dropbox():
    def __init__(self):
        APP_KEY = '30pb1xxpccvhfqo'
        APP_SECRET = 'kap2qg8dt2cp7cv'
        ACCESS_TYPE = 'app_folder'
        self.sess = session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)
        request_token = 's8123g2tz0fb73a'
        request_token_secret = 'kwsa9sapz264uq5'
        access_token = 'q6lds714ncu45k3'
        access_token_secret = 'elvc3gmgbw8b99f'
        self.sess.set_request_token(request_token,request_token_secret)
        self.sess.set_token(access_token,access_token_secret)
    def upload_and_share(self,stream):
        cli = client.DropboxClient(self.sess)
        image_io = StringIO(stream)
        response = cli.put_file('/eimg.png',image_io)
        results = cli.share(response['path'])
        return results['url']

class StreamService():
    def __init__(self):
        self.developer_key = "AI39si7wyQ0h6KhpWLhZfJa-U4mU65rO3Dj-05grmYkZk-kn_sv8br5UdDIEORwG-itcRn5wSBTFbgu02KyR_FhSQNaR0QbvSQ"
        self.client_id = google_api['client_id']
    def videos_by_user(self,username):
        uri = 'https://gdata.youtube.com/feeds/api/users/%s/uploads?alt=json' % username
        return self.do_request(uri)
    def video_thumbnail(self,token,access_token):
        actoken = self.refresh_google_token(access_token)
        uri = 'https://gdata.youtube.com/feeds/api/users/default/uploads/%s?access_token=%s' % (token,actoken)
        thumbnail = parseString(self.do_request(uri)).getElementsByTagName('media:thumbnail')[0].attributes['url'].value
        return str(thumbnail)
    def video_entry(self,title,description,keywords,access_token):
        media_group = gdata.media.Group(title=gdata.media.Title(text=title),
                                        description=gdata.media.Description(description_type='plain',text=description),
                                        keywords=gdata.media.Keywords(text='efforia'),
                                        category=[gdata.media.Category(text='Entertainment',
                                                                       scheme='http://gdata.youtube.com/schemas/2007/categories.cat',
                                                                       label='Entertainment')],
                                        player=None)
                                        #private=gdata.media.Private())
        video_entry = gdata.youtube.YouTubeVideoEntry(media=media_group) 
        url,token = self.get_upload_token(video_entry,access_token)
        return url,token
    
    def get_upload_token(self,video_entry,access_token):
        actoken = self.refresh_google_token(access_token)
        print actoken
        headers = {
                   'Authorization': 'OAuth %s' % actoken,
                   'X-gdata-key': 'key=%s' % self.developer_key,
                   'Content-type': 'application/atom+xml'
        }
        response = self.do_request('https://gdata.youtube.com/action/GetUploadToken',str(video_entry),headers)
        print response
        url = parseString(response).getElementsByTagName('url')[0].childNodes[0].data
        token = parseString(response).getElementsByTagName('token')[0].childNodes[0].data
        return url,token
        
    def search_video(self,search_terms):
        pass
