"""
GrooveWalrus: Pre-Fetch
Copyright (C) 2010
11y3y3y3y43@gmail.com
gardener@turnip-town.net
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

import wx
import os
from main_utils import system_files
from main_utils import file_cache
from main_utils import local_songs
from main_utils import tinysong

# cycle through playlist from current song
# if found as local file skip
# check if cached
# not cached, download

class PreFetch(object):
    def __init__(self, parent):
        self.parent = parent
        
    def GetNextSong(self):
        #find next non-local, non-cached file
        #currently playing track
        #self.parent.current_track
        for playlist_number in range(self.parent.current_track, self.parent.lc_playlist.GetItemCount(), 1):
            artist =    self.parent.lc_playlist.GetItem(playlist_number, 0).GetText()
            track =     self.parent.lc_playlist.GetItem(playlist_number, 1).GetText()
            album =     self.parent.lc_playlist.GetItem(playlist_number, 2).GetText()
            song_id =   self.parent.lc_playlist.GetItem(playlist_number, 3).GetText()

            # *** duplicating playsong()
            if (len(artist) > 0) & (len(track) > 0): #(song_id =='') & (len(artist) > 0) & (len(track) > 0):
                # query for song id, so we can play the file
                query_string = artist + ' ' + track
                #print query_string
                # check locally for song
                #query_results = local_songs.GetResults(query_string, 1)
                query_results = local_songs.DbFuncs().GetResultsArray(query_string, 1, True)
                if len(query_results) == 1:
                    song_id = query_results[0][4]
                #check if file exists
                if os.path.isfile(song_id):
                    pass
                else:
                    temp_dir = system_files.GetDirectories(self).TempDirectory()
                    file_name_plain = artist + '-' + track + '.mp3'
                    # don't clean cache dir, might try to delete the currently playing song
                    #file_cache.CheckCache(temp_dir)
                    # check if file previously cached
                    cached_file = file_cache.CreateCachedFilename(temp_dir, file_name_plain)
                    cached_file_name = cached_file[0]
                    if cached_file[1] == False:
                        # download this file
                        return (artist, track, cached_file_name)

    def GetSongId(self, artist, track):
    # use tinysong to find the song id
    # THIS SHOULD ALL BE SOMEWHERE ELSE, IT'S DUPLICATING STUFF IN gw.py
            
        query_results = tinysong.Tsong().get_search_results(artist + ' ' + track, 32)
        
        if len(query_results) >= 1:                
            # song id is at [1] - 4,2,6,1
            song_id = query_results[0]['SongID']
            
            # check for song match
            song_id2 = None
            if track.upper() != query_results[0]['SongName'].upper():
                #cylce through results to see if we can get and exact match
                #otherwise use the first result
                found_it = False
                for x in range(1, len(query_results) - 1):
                    if (query_results[x]['SongName'].upper() == track.upper()) & (found_it != True):
                        song_id2 = query_results[x]['SongID']
                        found_it = True
                        break
                        
            # check for artist match, if there's not a song match
            if (artist.upper() != query_results[0]['ArtistName'].upper()) & (song_id2 == None):
                # cycle through till will hit the right artist
                found_it = False
                for x in range(1, len(query_results) - 1):
                    if (query_results[x]['ArtistName'].upper() == artist.upper()) & (found_it != True):
                        song_id = query_results[x]['SongID']
                        found_it = True
                        break
            else:
            # we found the same song title match, lets use that
                if song_id2 != None:
                    song_id = song_id2
            
        return song_id