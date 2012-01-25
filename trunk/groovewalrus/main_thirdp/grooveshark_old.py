##Grooveshark.py

'''
Main class for handling of grooveshark

one grooveshark instance represents one session (so usually one per application instance)

GrooveWalrus: Taken from Zimmmer: http://hak5.org/forums/index.php?showtopic=14853&st=40
'''
#import time
#import sys
import uuid
import hashlib
import urllib
#import os
#import subprocess
#from mutagen.mp3 import MP3

from main_thirdp import urlgrabber
from main_utils import system_files
#import urlgrabber.progress


#Third Pary Libaries
from main_thirdp import httplib2 #Need version 5 or higher for python 2.6 compatability  - No version info in httplib2 so I can not check this :(

#try:
#    import json
#except ImportError:
from main_thirdp import simplejson as json
#import simplejson as json #If this also errors allows the gui/user/whatever to handle the failed import


#This is a default header that can be used if you just need a user agent change (this way not every function/method has to define this)
HEADER = {}
HEADER['user-agent'] = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3 (.NET CLR 3.5.30729)'

'''
Intialize Grooveshark
-- Get Session Data No Return
-- set ID3 tags No Return
-- Work methods
    - search, return json search results
    - songKeyfromID return songKey
    - Download - return song

Usage
g = Grooveshark()
g.getSessiondata()
-Searching
g.search('some search string')
-Get Song Key
g.getSongkeyFromID(songID)
-Download
g.Download(songKey)
-Popular Songs
g.Popular()

'''
CLIENTREVISION = "20091209.18"


class Grooveshark(object):
    def __init__(self, parent):
        self.search_url = 'http://cowbell.grooveshark.com/more.php?getSearchResults'
        self.count = 0
        self.parent = parent
        self.clientRevision = CLIENTREVISION
        
    def save(self, content, path):
        file_ = open(path, 'wb')
        file_.write(content)
        file_.close()
        
    def sessionData(self):
        self.session = self.getSessionID()
        self.uuid = self.getUID()
        self.token = self.getToken()
        
    def getToken(self):
        http = httplib2.Http()
        url = 'https://cowbell.grooveshark.com/service.php'
        self.secretKey = hashlib.md5(self.session).hexdigest()
        tokenPOSTdata = ('''{"header":{"session":"%s","uuid":"%s","client":"gslite","clientRevision":"%s"},'''
        '''"parameters":{"secretKey":"%s"},"method":"getCommunicationToken"}''' % (self.session, self.uuid, self.clientRevision, self.secretKey))
        request, reply = http.request(url, 'POST', headers = HEADER, body = tokenPOSTdata)
        return json.loads(reply)['result']
        
    def getUID(self):
        return uuid.uuid4()
        
    def getSessionID(self):
        http = httplib2.Http()
        url = 'http://listen.grooveshark.com'
        response, src = http.request(url, 'GET', headers = HEADER)
        src = src.lower().replace(' ', '')
        start = src.find('session')
        end = src[start:].find("',")
        startSession =  src[start:end+start].find("'") +1
        return src[startSession+start:end+start]
#work Methods

    def search(self, search_string):
        http = httplib2.Http()
        data = ('''{"header":{"session":"%s","uuid":"%s","client":"gslite","clientRevision":"%s","token":"%s"},'''
        '''"parameters":{"type":"Songs","query":"%s"},"method":"getSearchResults"}''' % (self.session, self.uuid, self.clientRevision, self.token, search_string.lower()))
        self.response, self.result = http.request(self.search_url, 'POST', headers = header, body = data)
        self.result = self.result
        self.searchResults = json.loads(self.result)['result']['Return']
        return self.searchResults
        
    def songKeyfromID(self, id):
        http = httplib2.Http()
        self.songID = id
        songKeyURL = '  http://cowbell.grooveshark.com/more.php?getStreamKeyFromSongID'
        songKeyPOSTdata = ('''{"header":{"token":"%s","session":"%s","uuid":"%s","client":"gslite","clientRevision":"%s"},'''
        '''"parameters":{"songID":%s,"prefetch":false},"method":"getStreamKeyFromSongID"}''') % (self.token, self.session, self.uuid, self.clientRevision, self.songID)
        request, reply = http.request(songKeyURL, 'POST', headers = HEADER, body = songKeyPOSTdata)
        self.reply = json.loads(reply)['result']
        print reply
        streamServer = self.reply['result']['streamServer']
        self.songKey = self.reply['result']['streamKey']
        return (self.songKey, streamServer)
        
    def download(self, songKey, streamServer, file_name, proxy=None):
        http = httplib2.Http()
        #use self. so that any outer program can access it (not local)
        self.mp3URL = 'http://'+streamServer+'/stream.php'
        data = {}
        data['streamKey'] = songKey
        #@@songHeader = dict(header)        
        #@@songHeader['content-length'] = str(len(urllib.urlencode(data)))
        #@@songHeader['content-type'] = 'application/x-www-form-urlencoded'
        #@@response, self.song = http.request(self.mp3URL, 'POST', headers = songHeader, body = urllib.urlencode(data))
        #@@print response        
        
        #{'content-length': '30', 'content-type': 'application/x-www-form-urlencoded', 'u
        #ser-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.1.3) Gecko/2
        #0090824 Firefox/3.5.3 (.NET CLR 3.5.30729)'}
        
        # using urlgrabber to grab the file, more responsive than httplib2, 
        # file saves as it downloads as opposed to when completed
        headers = (('content-length', str(len(urllib.urlencode(data)))), ('content-type', 'application/x-www-form-urlencoded'), ('user-agent', HEADER['user-agent']),)
        #prog = urlgrabber.progress.text_progress_meter()        
        #response = urlgrabber.urlopen(self.mp3URL, data=urllib.urlencode(data), http_headers=headers) #, progress_obj=prog)
        #response = urlgrabber.urlread(self.mp3URL, data=urllib.urlencode(data), http_headers=headers) #, progress_obj=prog)
        #file_name = system_files.GetDirectories(self.parent).BuildTempFile('temp.mp3')
        #proxies={ 'http' : 'http://foo:3128', 'https' : 'http://foo:3128' }
        proxy_dict = None
        if proxy != None:
            proxy_dict = {'http' : proxy}
        response = urlgrabber.urlgrab(self.mp3URL, filename=file_name, data=urllib.urlencode(data), http_headers=headers, proxies=proxy_dict)
        
        #if self.response['status'] == '302':
        #    self.response, self.song = http.request(self.response['location'], 'GET', headers = header)
        #    print 'BOO'
        #if self.response['status'] == '400':
        #    return '400 Error'
        #@@f = open('temp.mp3', 'wb')
        #@@f.write(self.song)
        #@@f.close()
        return response

    def GetFileSize(self, songKey, streamServer, proxy=False):
        http = httplib2.Http()
        url = 'http://'+streamServer+'/stream.php'#use self. so that any outer program can access it (not local)
        params = urllib.urlencode({'streamKey': songKey})
        
        if proxy:
            f = proxy.open(url, params)       
        else:
            f = urllib.urlopen(url, params)
        file_size = f.info().dict['content-length']
        return file_size 
    
    def stream(self, streamKeys, songServers, file):
        '''A list of streamkeys and base file'''
        #self.stream_process = subprocess.Popen('python stream.py %s %s %s' % (json.dumps(songServers), json.dumps(streamKeys), file))
        pass
        
    def popular(self):
        http = httplib2.Http()
        url = 'http://cowbell.grooveshark.com/more.php?popularGetSongs'
        popularPOSTdata = ('''{"header":{"token":"%s","session":"%s","uuid":"%s","client":"gslite","clientRevision":"%s"},'''
        '''"parameters":{},"method":"popularGetSongs"}''' % (self.token, self.session, self.uuid, self.clientRevision))
        request, reply = http.request(url, 'POST', headers = HEADER, body = popularPOSTdata)
        return json.loads(reply)['result']['Songs']

    # def favorites(self):
        # http = httplib2.Http()
        # url = 'http://cowbell.grooveshark.com/more.php?getFavorites'
        # songKeyPOSTdata = ('''{"header":{"token":"%s","session":"%s","uuid":"%s","client":"gslite","clientRevision":"20091209.18"},'''
        # '''"parameters":{"prefetch":false},"method":"getFavorites"}''' % (self.token, self.session, self.uuid))
        # request, reply = http.request(url, 'POST', headers = header, body = songKeyPOSTdata)
        # print request
    # def playlist(self):
        # http = httplib2.Http()
        # url = 'http://cowbell.grooveshark.com/more.php?playlistGetSongs'
        # songKeyPOSTdata = ('''{"header":{"token":"%s","session":"%s","uuid":"%s","client":"gslite","clientRevision":"20091209.18"},'''
        # '''"parameters":{"prefetch":false},"method":"getPaylist"}''' % (self.token, self.session, self.uuid))
        # request, reply = http.request(url, 'POST', headers = header, body = songKeyPOSTdata)
        # print request

    def setID3tags(self, file, title = None, artist = None, album = None, albumArt = None, genre = None, composer = None):
        '''Does NOT WORK DUE TO UNKOWN UNICODE PROBLEM when saving'''
        #if not os.path.exists(file):
        #    raise IOError('MP3 File does not exist.')
        #print file
        #tag_lookup = {'album':'TALB', 'comment':"COMM::'eng'", 'description':'TIT3', 'artist':'TPE1', 'title':'TIT2', 'track':'TRCK', 'composer':'TCOM', 'genre':'TCON'}
        #http = httplib2.Http()
        #request, albumArt = http.request('http://beta.grooveshark.com/static/amazonart/'+albumArt)
        #if request['status'] == '404':
        #    albumArt = u''
        #tag_lookup['album_art'] = 'TART'
        #tags = {}
        #tags['title'] = title
        #tags['artist'] = artist
        #tags['album'] = album
        #tags['album_art'] = albumArt
        #tags['genre'] = genre
        #tags['composer'] = composer
        #if tags['composer'] == None:
        #    tags['composer'] = tags['artist']
        #for i in tags:
        #    if tags[i] == None:
        #        tags[i] = ''
        #audio = MP3(file)
        #Delete Existing Songs
        #audio.delete()
        #Set the tags
        #Iterate through tags
        #for i in tags:
        #    print i
        #    print type(tags[i])
        #    print tags[i]
        #    audio[tag_lookup[i]] = tags[i]
        #print audio[tag_lookup[i]]
        #audio.tags.save()
        pass