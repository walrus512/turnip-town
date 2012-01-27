"""
GrooveWalrus: Musicbrainz
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

#<metadata>
#<track-list count="20" offset="0">
#<track id="9b72ea5b-0cd4-4cfd-8952-728f79d350a7" ext:score="100">
#<title>White Room</title>
#<duration>301466</duration>
#<artist id="618b6900-0618-4f1e-b835-bccb17f84294">
#<name>Eric Clapton</name>
#</artist>
#<release-list>
#<release id="ced79c7e-0db0-496e-9b85-a09c30406b79">
#<title>The Best of Eric Clapton</title>
#<track-list offset="6" count="17"/>
#</release>
#</release-list>
#</track>
#</track-list>
#</metadata>

# get release id
# http://musicbrainz.org/ws/1/track/?type=xml&limit=1&title=White+room&artist=Eric+clapton
# get release tracks
# http://musicbrainz.org/ws/1/release/ced79c7e-0db0-496e-9b85-a09c30406b79?type=xml&limit=1&inc=tracks

TRACK_GETINFO = "http://musicbrainz.org/ws/1/track/?type=xml&limit=5" #&releasetype=album"
ALBUM_GETINFO = "http://musicbrainz.org/ws/1/release/?type=xml&limit=1"
RELEASE_GETINFO = "http://musicbrainz.org/ws/1/release/"


class AudioScrobblerError(Exception):
    pass
    
# ===================================================================
class Brainz(object):
    def __init__(self):
        self.last_file_name = ''
        
    def read_xml_tree(self, file_name):
        # reads in an xml file and returns a blob for you to work with
        urllib.URLopener.version = 'GrooveWalrus/0.3 ( http://groove-walrus.turnip-town.net )'
        tree = ''
    	try:
        	tree = ET.parse(urllib.urlopen(file_name))
       	except Exception, inst:
       	     print 'Exception: musicbrainz: ' + str(inst)        
        #ET.dump(tree)
        return tree        
        
    def get_song_time(self, artist, track):
        # http://musicbrainz.org/ws/1/track/?type=xml&limit=1&title=White+room&artist=Eric+clapton
        # get the album id for the track
        # <metadata <track-list <track <release-list <release id="sdgsdg" <title
        song_seconds = 0
        artist = url_quote(artist)
        track = url_quote(track)
        data_url = TRACK_GETINFO + "&artist=" + artist + "&title=" + track
        data_url = data_url.lower()
        tree = self.read_xml_tree(data_url.replace(' ', '%20'))
        # 
        #print data_url
        if tree !='':
            root = tree.getroot() # 
            sub_root = root.getchildren() #<metadata>
            
            #print sub_root[0]
            try:
                ele_tracklist = sub_root[0].getchildren() #<tracklist>        
                #ele_track = ele_tracklist[0].getchildren() #<track>
                #print ele_tracklist
                #print ele_track
                #print len(ele_tracklist) 
                for track in ele_tracklist:
                    #print track
                    durs = track.find('{http://musicbrainz.org/ns/mmd-1.0#}duration')                
                    try:
                       song_seconds = int(durs.text) / 1000
                       print durs.text
                       break
                    except AttributeError:
                        pass
    
                #for x in ele_track:
                #    if (x.tag[-8:] == 'duration'):
                #        #print x.text
                #        song_seconds = int(x.text) / 1000
                                        
            except IndexError:
                pass
        
        return song_seconds
        
                
    def get_song_info(self, artist, track):
        # http://musicbrainz.org/ws/1/track/?type=xml&limit=1&title=White+room&artist=Eric+clapton
        # get the album id for the track
        # <metadata <track-list <track <release-list <release id="sdgsdg" <title
        release_id = ''
        album_name = ''
        artist = url_quote(artist)
        track = url_quote(track)
        data_url = TRACK_GETINFO + "&artist=" + artist + "&title=" + track
        tree = self.read_xml_tree(data_url.replace(' ', '+'))
        # 
        print data_url
        if tree !='':
            root = tree.getroot() # 
            sub_root = root.getchildren() #<metadata>
            try:
                ele_tracklist = sub_root[0].getchildren() #<tracklist>        
                ele_track = ele_tracklist[0].getchildren() #<track>
                #print ele_tracklist
    
                for x in ele_track:
                    if (x.tag[-12:] == 'release-list'):
                        ele_relaselist = x.getchildren() #<release-list
                        ele_release = ele_relaselist[0].getchildren() #<release
                        release_attrib = ele_relaselist[0].attrib
                        # get the id attribute of the release tag
                        release_id = release_attrib['id']
                        #print release_id
                        for y in ele_release:
                            if (y.tag[-5:] == 'title'):
                                album_name = y.text
                                # print album_name
                                        
            except IndexError:
                pass
            
        return [release_id, album_name]

    def get_album_info(self, artist, album):
        # http://musicbrainz.org/ws/1/track/?type=xml&limit=1&title=White+room&artist=Eric+clapton
        # get the album id for the track
        # <metadata <track-list <track <release-list <release id="sdgsdg" <title
        release_id = ''
        album_name = ''
        data_url = ALBUM_GETINFO + "&artist=" + artist + "&title=" + album
        tree = self.read_xml_tree(data_url.replace(' ', '+'))
        # 
        #print data_url
        if tree !='':
            root = tree.getroot() #
            sub_root = root.getchildren() #<metadata>
            #print sub_root
            try:
                #ele_tracklist = sub_root[0].getchildren() #<tracklist>        
                #ele_track = ele_tracklist[0].getchildren() #<track>
                #print ele_tracklist
    
                for x in sub_root:
                    if (x.tag[-12:] == 'release-list'):
                        ele_relaselist = x.getchildren() #<release-list
                        ele_release = ele_relaselist[0].getchildren() #<release
                        release_attrib = ele_relaselist[0].attrib
                        # get the id attribute of the release tag
                        release_id = release_attrib['id']
                        #print release_id
                        for y in ele_release:
                            if (y.tag[-5:] == 'title'):
                                album_name = y.text
                                # print album_name
                                        
            except IndexError:
                print 'mbz:indexerror'
        
        return [release_id, album_name]
        
        
    def get_track_list(self, mbid):
        # http://musicbrainz.org/ws/1/release/290e10c5-7efc-4f60-ba2c-0dfc0208fbf5?type=xml&inc=tracks
        # get the track list for the album, music brainz id
        # <metadata <release <track-list <track <title        
        album_list = []
        data_url = RELEASE_GETINFO + mbid + '?type=xml&inc=tracks'
        tree = self.read_xml_tree(data_url.replace(' ', '+'))
        # 
        print data_url
        if tree !='':
            root = tree.getroot() # 
            sub_root = root.getchildren() #<metadata>
            #ele_release = sub_root[0].getchildren() #<release>
            try:
                ele_track_list = sub_root[0].find('{http://musicbrainz.org/ns/mmd-1.0#}track-list')
                #print ele_track_list
                ele_track = ele_track_list.getchildren()
                counter = 1
    
                for x in ele_track:
                    #print x.tag
                    if (x.tag[-5:] == 'track'):
                        y = x.find('{http://musicbrainz.org/ns/mmd-1.0#}title')
                        
                        counter = counter + 1
                        ele_track_details = x.getchildren()
                        artist_name = ''
                        for g in ele_track_details:
                            if (g.tag[-6:] == 'artist'):
                                artist = g.find('{http://musicbrainz.org/ns/mmd-1.0#}name')
                                artist_name = artist.text
                        album_list.append((y.text, artist_name))
            except IndexError:
                pass
                
        return album_list

  
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

              
