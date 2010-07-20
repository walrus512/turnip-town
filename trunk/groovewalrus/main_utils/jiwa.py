"""
GrooveWalrus: Jiwa.fm Search 
Copyright (C) 2010
11y3y3y3y43@gmail.com
http://groove-walrus.turnip-town.net
-----
This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 2 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program; if not, write to the Free Software Foundation, Inc., 59 Temple
Place, Suite 330, Boston, MA 02111-1307 USA
"""
import urllib
import hashlib

try:
    import json
except ImportError:
    from main_thirdp import simplejson as json
    
JIWA_SEARCH = "http://www.jiwa.fm/track/search"
JIWA_TOKEN = "http://m.jiwa.fm/token.php"
JIWA_FLASH = "http://www.jiwa.fm/res/widget/monotitle.swf?skin=round&trackId="
JIWA_MP3 = "http://m.jiwa.fm/play.php?r="

class JiwaMusic():
    def __init__(self):
    	pass
    	
    def GetSearchResults(self, artist, song):
    	#http://www.jiwa.fm/track/search
    	#post q="query string", noRestricted=true
    	search_string = artist + ' ' + song
    	url_connection = urllib.urlopen(JIWA_SEARCH, 
    	    data=urllib.urlencode({'q': search_string, 'noRestricted': 'true'}))
        raw_results = url_connection.read()
        
        results_array = json.loads(raw_results)

        ##counter = 0
        # cycle through the results and string any integers
        ##print results_array['page']
        ##for x in results_array['page']:            
            #cycle through each dictionary
            ##for key, value in x.items():
               ##print key
               ##print value
               ## if IsInteger(value):
                ##     results_array[counter][key] = str(value)
           ## counter = counter + 1
        ##print results_array
        #need track_id and song_id for later
        #songId, trackId, songName, artistName, albumName
        
        return results_array['page']
        
        #{"page":[{"trackId":1345600,"songId":369589,
        #"songName":"One","artistId":2506,"artistName":"U2",
        #"secArtistsNames":null,"albumId":122237,"albumName":"Achtung Baby",
        #"songPopularity":907500,"itunesTrackUrl":"http:\/\/itunes.apple.com\/fr\/album\/one\/id14771942?i=14771950&uo=4&partnerId=2003",
        #"starzikTrackUrl":"http:\/\/www.starzik.com\/mp3\/titres\/One-964825.html?partner=20895",
        #"albumReleaseDate":"2002-05-27",
        #"duration":276,"hidden":false,
        #"sourceId":"100","territory":null,"style":null,
        #"styleSecondary":null,"restricted":"0"},
        #{"trackId":3387316,"songId":477869, ...

    def GetFlashUrl(self, track_id):
        #http://www.jiwa.fm/res/widget/monotitle.swf?trackId=369589&skin=round
        return JIWA_FLASH + str(track_id)
        
    def GetFlashUrlFirstResult(self, artist, song):
        #http://www.jiwa.fm/res/widget/monotitle.swf?trackId=369589&skin=round
        results_array = self.GetSearchResults(artist, song)
        print results_array
        if len(results_array) > 1:
            track_id = results_array[0]['trackId']
        else:
            track_id = 1345600
            song_id = 369589
            url = self.GetMp3Url(str(track_id), str(song_id))
            print self.GetFileSize(url)
            
        return JIWA_FLASH + str(track_id)

    def GetToken(self, track_id):
        #get the token, pass trackid
        #token
        #'1e234534aaf8dc3693d2b3550bf6fa4c=90614697=0=2164577=167=OK'
        url_connection = urllib.urlopen(JIWA_TOKEN,
            data=urllib.urlencode({'s': track_id, 'r':'1'}))
        raw_results = url_connection.read()
        print raw_results
        results = raw_results.split('=')        
        return results
        
    def GetMp3Url(self, track_id, song_id):
        #generate the download url
        #4e91863e5a29c5197581fcaf621bb520=90614819=0=1188566=276=OK
        #/play.php?r=90614819&s=369589&t=230b11aec8405a9cc9a82d1289a6881a&m=1188566&from=0
        
        token_array = self.GetToken(track_id)

        url = ''
        if (len(token_array) > 0):        
            a = hashlib.md5('gwqd29ydg7sqys_qsh0').hexdigest()
            b = hashlib.md5(token_array[0] + a + song_id).hexdigest()
            url = JIWA_MP3 + token_array[1] + "&s=" + song_id + "&t=" + b + "&m=" + token_array[3] + "&from=0"
        print url
        return url
        
    def DownloadFile(self, songKey, streamServer, file_name):
        #http = httplib2.Http()
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
        response = urlgrabber.urlgrab(self.mp3URL, filename=file_name, data=urllib.urlencode(data), http_headers=headers)
        
        #if self.response['status'] == '302':
        #    self.response, self.song = http.request(self.response['location'], 'GET', headers = header)
        #    print 'BOO'
        #if self.response['status'] == '400':
        #    return '400 Error'
        #@@f = open('temp.mp3', 'wb')
        #@@f.write(self.song)
        #@@f.close()
        return response

    def GetFileSize(self, url):
        #http = httplib2.Http()
        #url = 'http://'+streamServer+'/stream.php'#use self. so that any outer program can access it (not local)
        params = '' #urllib.urlencode({'streamKey': songKey})
        f = urllib.urlopen(url, params)
        print f.info()
        print f.read()
        file_size = f.info().dict['content-length']
        return file_size 
        
                
#---------------------------------
#---------------------------------
def IsInteger(x):
    try:
        if int(x) == x:
            return True
    except:
        return False
        
#----------------------------------
#class SearchThread(Thread):
    #
    #def __init__(self, ):        
    #    pass
        
    #def run(self):
    #    pass
        
#-----------------------------------
charset = 'utf-8'
        
def url_quote(s, safe='/', want_unicode=False):
    """
    Wrapper around urllib.quote doing the encoding/decoding as usually wanted:
    
    @param s: the string to quote (can be str or unicode, if it is unicode,
              config.charset is used to encode it before calling urllib)
    @param safe: just passed through to urllib
    @param want_unicode: for the less usual case that you want to get back
                         unicode and not str, set this to True
                         Default is False.
    """
    if isinstance(s, unicode):
        s = s.encode(charset)
    elif not isinstance(s, str):
        s = str(s)
    s = urllib.quote(s, safe)
    if want_unicode:
        s = s.decode(charset) # ascii would also work
    return s
    