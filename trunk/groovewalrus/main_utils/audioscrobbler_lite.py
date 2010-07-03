"""
GrooveWalrus: Audioscrobber Utils
Copyright (C) 2009
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
import xml.etree.ElementTree as ET


#<?xml version="1.0" encoding="utf-8"?>
#<lfm status="ok">
#<toptracks artist="Foals">
#    <track rank="1">
#        <name>Cassius</name>
#        <playcount>240299</playcount>
#        <mbid></mbid>
#        <url>http://www.last.fm/music/Foals/_/Cassius</url>

#        <streamable fulltrack="0">1</streamable>
#                <artist>
#            <name>Foals</name>
#            <mbid>6a65d878-fcd0-42cf-aff9-ca1d636a8bcc</mbid>
#            <url>http://www.last.fm/music/Foals</url>
#        </artist>
#                        <image size="small">http://userserve-ak.last.fm/serve/34s/5008171.jpg</image>
#        <image size="medium">http://userserve-ak.last.fm/serve/64s/5008171.jpg</image>
#        <image size="large">http://userserve-ak.last.fm/serve/126/5008171.jpg</image>
#            </track>


# http://ws.audioscrobbler.com/2.0/?method=artist.gettoptracks&api_key=g9g&artist=foals

API_KEY = "&api_key=13eceb51a4c2e0f825c492f04bf693c8"
TRACK_GETINFO =     "http://ws.audioscrobbler.com/2.0/?method=track.getinfo" + API_KEY
ALBUM_GETINFO =     "http://ws.audioscrobbler.com/2.0/?method=album.getinfo" + API_KEY
ARTIST_GETINFO =    "http://ws.audioscrobbler.com/2.0/?method=artist.getinfo" + API_KEY
ARTIST_TOP_SONGS =  "http://ws.audioscrobbler.com/2.0/?method=artist.gettoptracks" + API_KEY
ARTIST_TOP_ALBUMS = "http://ws.audioscrobbler.com/2.0/?method=artist.gettopalbums" + API_KEY
SONG_SIMILAR =      "http://ws.audioscrobbler.com/2.0/?method=track.getsimilar" + API_KEY
ARTIST_SIMILAR =    "http://ws.audioscrobbler.com/2.0/?method=artist.getsimilar" + API_KEY
GEO_TOP_SONGS =     "http://ws.audioscrobbler.com/2.0/?method=geo.gettoptracks" + API_KEY
PLAYLIST_FETCH =    "http://ws.audioscrobbler.com/2.0/?method=playlist.fetch" + API_KEY
GENRE_TOP_SONGS =   "http://ws.audioscrobbler.com/2.0/?method=tag.gettoptracks" + API_KEY
USER_TOP_SONGS =    "http://ws.audioscrobbler.com/2.0/?method=user.gettoptracks" + API_KEY
USER_FRIENDS =      "http://ws.audioscrobbler.com/2.0/?method=user.getfriends" + API_KEY
USER_NEIGHBOURS =   "http://ws.audioscrobbler.com/2.0/?method=user.getneighbours" + API_KEY
USER_RECENT_SONGS = "http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&limit=50" + API_KEY #&user=rj&api_key=b25b959554ed76058ac220b7b2e0a026"
SONG_TOP_TAGS =     "http://ws.audioscrobbler.com/2.0/?method=track.gettoptags" + API_KEY #&artist=cher&track=believe&api_key=b25b959554ed76058ac220b7b2e0a026
USER_LOVED_SONGS =  "http://ws.audioscrobbler.com/2.0/?method=user.getlovedtracks" + API_KEY #&user=rj&api_key=b25b959554ed76058ac220b7b2e0a026"

PER_TIMES = ['recent', '7day', '3month', '6month', '12month', 'overall']


class AudioScrobblerError(Exception):
    pass
    
# ===================================================================
class Scrobb(object):
    def __init__(self):
        self.last_file_name = ''
        self.last_similar_file_name = ''        
        self.last_country_name = ''
        
    def read_xml_tree(self, file_name):
        # reads in an xml file and returns a blob for you to work with
        tree = ''
    	try:
        	tree = ET.parse(urllib.urlopen(file_name))
       	except Exception, inst:
       	     print 'Exception: audioscrobber_lite: ' + str(inst)
        #ET.dump(tree)
        #print tree
        return tree    
            
# =================================================================== 
         
    def make_similar_song_list(self, artist, song):
        # gets settings from window settings file returns an object / settings
        # *** remeber last scrobbed album
        artist = url_quote(artist)
        song = url_quote(song)
        data_url = SONG_SIMILAR + "&artist=" + artist + "&track=" + song
        return self.genenric_song_list(data_url, 'name', 'match')
        
    def make_song_top_tags_list(self, artist, song):
        # returns top tags for selected song
        artist = url_quote(artist)
        song = url_quote(song)
        data_url = SONG_TOP_TAGS + "&artist=" + artist + "&track=" + song
        return self.genenric_song_list(data_url, 'name', 'count')
        
    def make_similar_artist_list(self, artist):
        # gets similar artists
        artist = url_quote(artist)
        data_url = ARTIST_SIMILAR + "&artist=" + artist
        return self.genenric_song_list(data_url, 'name', 'match')
            
    def make_artist_top_song_list(self, artist):
        # gets settings from window settings file returns an object / settings
        # *** remeber last scrobbed album
        #scrobb_url = "http://ws.audioscrobbler.com/2.0/?method=artist.gettoptracks&api_key=" + API_KEY + "&artist=" + artist
        #print(file_name.replace(' ', '%20'))
        artist = url_quote(artist)
        data_url = ARTIST_TOP_SONGS + "&artist=" + artist
        return self.genenric_song_list(data_url, 'name', 'listeners')
        
    def make_artist_top_album_list(self, artist):
        # gets top albums per artist
        artist = url_quote(artist)
        data_url = ARTIST_TOP_ALBUMS + "&artist=" + artist
        return self.genenric_song_list(data_url, 'name', 'playcount')
        
    def make_geo_top_song_list(self, country):
        # gets top songs per country
        #scrobb_url = "http://ws.audioscrobbler.com/2.0/?method=geo.gettoptracks&country=united+states&api_key=b25b959554ed76058ac220b7b2e0a026
        country = url_quote(country)
        data_url = GEO_TOP_SONGS + "&country=" + country
        return self.genenric_song_list(data_url, 'name', 'listeners')
        
    def make_genre_top_song_list(self, genre):
        # gets top songs per genre (tag)
        #scrobb_url = "http://ws.audioscrobbler.com/2.0/?method=geo.gettoptracks&country=united+states&api_key=b25b959554ed76058ac220b7b2e0a026
        genre = url_quote(genre)
        data_url = GENRE_TOP_SONGS + "&tag=" + genre
        return self.genenric_song_list(data_url, 'name', 'tagcount')
            
    def make_user_top_songs(self, user, tperiod=1):
        # gets recent played songs for user
        #recent| overall | 3month | 6month | 12month | 7day
        if PER_TIMES[tperiod] == 'recent':
            data_url = USER_RECENT_SONGS + "&user=" + user
            return self.genenric_song_list_two(data_url, 'artist', 'name', 'date')            
        else:
            data_url = USER_TOP_SONGS + "&user=" + user + "&period=" + PER_TIMES[tperiod]
            return self.genenric_song_list(data_url, 'name', 'playcount')
        
    def get_friends(self, user):
        # return a list of friends for user
        user = url_quote(user)
        data_url = USER_FRIENDS + "&user=" + user
        return self.genenric_song_list(data_url, 'name', 'url')

    def get_neighbours(self, user):
        # return a list of neighbours for user
        user = url_quote(user)
        data_url = USER_NEIGHBOURS + "&user=" + user
        return self.genenric_song_list(data_url, 'name', 'match')
        
    def get_loved_songs(self, user):
        # return a list of friends for user
        user = url_quote(user)
        data_url = USER_LOVED_SONGS + "&user=" + user
        return self.genenric_song_list(data_url, 'name', 'date')

# ===================================================================         
    def genenric_song_list(self, data_url, iterator_one, iterator_two):
        # returns the songs list        
        print data_url
        if (data_url != self.last_similar_file_name):        
            tree = self.read_xml_tree(data_url.replace(' ', '%20'))
            self.new_similar_tree = tree
        else:
            tree = self.new_similar_tree
        # make a blob of settings info
        root = tree.getroot() # <lfm>
        sub_root = root.getchildren() # <toptracks>
        tracks = sub_root[0].getchildren() # <track>
        song_list = []
        #print root
        #print sub_root
        #print file_name
        counter = 0

        for track in tracks:
            # makes a dictionary with xml tag / value pairs
            names = track.getiterator(iterator_one)
            match = track.getiterator(iterator_two)
            #cover_image = track.getiterator("image")
            #print(cover_image)

            name_list = []
            #song and artist
            for x in names:             
                name_list.append(x.text)
            # playcount
            if len(match) != 0:
                if match[0].text == None:
                    name_list.append('')
                else:
                    name_list.append(match[0].text)
            else:
                name_list.append('')
            #for y in cover_image:
            #   name_list.append(y.text)
            #print ET.tostring(x)
            song_list.append(name_list)
            counter = counter + 1
            
        self.last_similar_file_name = data_url
        
        return song_list
        
    def genenric_song_list_two(self, data_url, iterator_one, iterator_two, iterator_three):
        # returns the songs list        
        #print data_url.replace(' ', '%20')
        if (data_url != self.last_similar_file_name):        
            tree = self.read_xml_tree(data_url.replace(' ', '%20'))
            self.new_similar_tree = tree
        else:
            tree = self.new_similar_tree
        # make a blob of settings info
        root = tree.getroot() # <lfm>
        sub_root = root.getchildren() # <toptracks>
        tracks = sub_root[0].getchildren() # <track>
        song_list = []
        #print root
        #print sub_root
        #print file_name
        counter = 0

        for track in tracks:
            # makes a dictionary with xml tag / value pairs
            artists = track.getiterator(iterator_one)
            names = track.getiterator(iterator_two)
            match = track.getiterator(iterator_three)
            #cover_image = track.getiterator("image")
            #print(cover_image)

            name_list = []
            #song and artist
            #for x in names:             
            #    name_list.append(x.text)
            # playcount
            name_list.append(names[0].text)
            name_list.append(artists[0].text)            
            if len(match) > 0:
                name_list.append(match[0].text)
            else:
                name_list.append('Now playing')
            #for y in cover_image:
            #   name_list.append(y.text)
            #print ET.tostring(x)
            song_list.append(name_list)
            counter = counter + 1
            
        self.last_similar_file_name = data_url
        
        return song_list
        
    def make_album_top_song_list(self, artist, album):
        # get album id
        artist = url_quote(artist)
        album = url_quote(album)
        album_id = ''
        data_url = ALBUM_GETINFO + "&artist=" + artist + "&album=" + album
        #print data_url
        tree = self.read_xml_tree(data_url.replace(' ', '+'))
        # 
        root = tree.getroot() # <lfm>
        sub_root = root.getchildren() # various <tags>

        #print sub_root
        try:
            album_elements = sub_root[0].getchildren()
            #print album_elements
            for x in album_elements:
                #print x.tag
                if (x.tag == 'id'):
                    album_id = x.text
        except AttributeError:
            pass

        # get track list
        #&playlistURL=lastfm://playlist/album/2026126
        data_url2 = PLAYLIST_FETCH + "&playlistURL=lastfm://playlist/album/" + album_id
        if len(album_id) > 0:
            tree = self.read_xml_tree(data_url2)
            root = tree.getroot() # <lfm>
            sub_root = root.getchildren() # <playList>
            # *** this is bad
            tracklist = sub_root[0].find('{http://xspf.org/ns/0/}trackList') # <track>
            tracks = tracklist.getchildren()
            song_list = []
            #print root
            #print sub_root
            #print file_name
            counter = 0

            for track in tracks:
                # makes a dictionary with xml tag / value pairs
                #print track
                song = track.getiterator('{http://xspf.org/ns/0/}title')
                artist = track.getiterator('{http://xspf.org/ns/0/}creator')
                #album = track.getiterator('{http://xspf.org/ns/0/}album')

                name_list = []
                #song and artist
                name_list.append(song[0].text)
                name_list.append(artist[0].text)
                # playcount
                # now we have to get the play count for each song in the album
                # and sort it
                ##playcount = self.get_play_count(artist[0].text, song[0].text)
                name_list.append('')
                song_list.append(name_list)
                counter = counter + 1
            
            self.last_similar_file_name = data_url        
            return song_list        
        
# ===================================================================         
# ===================================================================  
       
    def get_play_count(self, artist, track):
        # http://ws.audioscrobbler.com/2.0/?method=track.getinfo&api_key=b25b959554ed76058ac220b7b2e0a026&artist=cher&track=believe
        # get an image for track requested
        # <lfm <album <image
        track = url_quote(track)
        playcount = ''
        data_url = TRACK_GETINFO + "&artist=" + artist + "&track=" + track
        #print data_url
        tree = self.read_xml_tree(data_url.replace(' ', '+'))
        # 
        root = tree.getroot() # <lfm>
        sub_root = root.getchildren() # various <tags>
        try:
            playcount_ele = sub_root[0].find('playcount')
            playcount = playcount_ele.text
        except AttributeError:
            pass

        return playcount
 
    def get_artist_bio(self, artist):
        #
        # <lfm <artist <bio <summary
        #print file_name
        artist = url_quote(artist)
        summary_text = ''
        image_url = ''
        data_url = ARTIST_GETINFO + "&artist=" + artist
        tree = self.read_xml_tree(data_url.replace(' ', '+'))
        #
        if tree !='':
            root = tree.getroot() # <lfm>
            sub_root = root.getchildren() # various <tags>
            try:
                artist_elements = sub_root[0].getchildren()
                #print album_elements
                for x in artist_elements:
                    #print x
                    if (x.tag == 'image'):
                        image_url = x.text
                    if (x.tag == 'bio'):
                        y = x.find('summary')
                        summary_text = y.text
                    #print summary_text
            except AttributeError:
                pass

        return (image_url, summary_text)

    def get_song_art(self, artist, track):
        # http://ws.audioscrobbler.com/2.0/?method=track.getinfo&api_key=b25b959554ed76058ac220b7b2e0a026&artist=cher&track=believe
        # get an image for track requested
        # <lfm <album <image
        artist = url_quote(artist)
        track = url_quote(track)
        image_url = ''
        data_url = TRACK_GETINFO + "&artist=" + artist + "&track=" + track
        #print data_url
        tree = self.read_xml_tree(data_url.replace(' ', '+'))
        #
        if tree !='':
            root = tree.getroot() # <lfm>
            sub_root = root.getchildren() # various <tags>
            try:
                album_elements = sub_root[0].find('album').getchildren()
                #print album_elements
                for x in album_elements:
                    #print x
                    if (x.tag == 'image'):
                        image_url = x.text
            except AttributeError:
                pass

        return image_url
        
    def get_album_art(self, artist, album):
        # http://ws.audioscrobbler.com/2.0/?method=track.getinfo&api_key=b25b959554ed76058ac220b7b2e0a026&artist=cher&track=believe
        # get an image for track requested
        # <lfm <album <image
        artist = url_quote(artist)
        album = url_quote(album)
        image_url = ''
        data_url = ALBUM_GETINFO + "&artist=" + artist + "&album=" + album
        #print data_url
        tree = self.read_xml_tree(data_url.replace(' ', '+'))
        #
        if tree !='':
            root = tree.getroot() # <lfm>
            sub_root = root.getchildren() # various <tags>
    
            #print sub_root
            try:
                album_elements = sub_root[0].getchildren()
                #print album_elements
                for x in album_elements:
                    #print x.tag
                    if (x.tag == 'image'):
                        image_url = x.text
            except AttributeError:
                pass

        return image_url
        
    def get_song_info(self, artist, track):
        #<toptags<tag<name
        #<listeners
        #<playcount
        artist = url_quote(artist)
        track = url_quote(track)
        playcount = ''
        listeners = ''
        top_tag = ''
        data_url = TRACK_GETINFO + "&artist=" + artist + "&track=" + track
        #print data_url
        tree = self.read_xml_tree(data_url.replace(' ', '+'))
        #
        if tree !='': 
            root = tree.getroot() # <lfm>
            sub_root = root.getchildren() # various <tags>
            try:
                playcount_ele = sub_root[0].find('playcount')
                playcount = playcount_ele.text
                listeners_ele = sub_root[0].find('listeners')
                listeners = listeners_ele.text
                
                if len(sub_root[0].find('toptags').getchildren()) >= 1:
                    toptags_ele = sub_root[0].find('toptags').getchildren()[0].find('name')    
                    top_tag = toptags_ele.text
            except AttributeError:
                pass
            #print toptags_ele
            #print playcount
            #print listeners
            #print data_url
        return (playcount, listeners, top_tag)
        
# ===================================================================            

              
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
     
# ===================================================================            
