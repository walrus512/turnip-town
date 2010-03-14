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
                    song_id = str(query_results[0][4])
                #check if file exists
                if os.path.isfile(song_id):
                    pass
                else:
                    temp_dir = system_files.GetDirectories(self).TempDirectory()
                    file_name_plain = artist + '-' + track + '.mp3'
                    # clean cache dir
                    file_cache.CheckCache(temp_dir)
                    # check if file previously cached
                    cached_file = file_cache.CreateCachedFilename(temp_dir, file_name_plain)
                    cached_file_name = cached_file[0]
                    if cached_file[1] == False:
                        # download this file
                        return (artist, track)
                
"""                
                        query_results = tinysong.Tsong().get_search_results(query_string, 32)
                        split_array = query_results[0].split('; ')
                        if len(split_array) >= 2:                
                            # song id is at [1] - 4,2,6,1
                            song_id = split_array[1]
                            # let's check for album and update that too
                            if (album =='') & (split_array[6] != ''):
                                album = split_array[6]
                                self.parent.lc_playlist.SetStringItem(playlist_number, 2, album)
                            #print artist
                            #print split_array[4]
                            
                            # check for song match
                            if track.upper() != split_array[2].upper():
                                #cylce through results to see if we can get and exact match
                                #otherwise use the first result
                                found_it = False
                                for x in range(1, len(query_results) - 1):
                                    y = query_results[x].split('; ')
                                    #print y
                                    if (y[2].upper() == track.upper()) & (found_it != True):
                                        song_id = y[1]
                                        self.parent.lc_playlist.SetStringItem(playlist_number, 3, song_id)
                                        self.parent.SavePlaylist(self.parent.main_playlist_location)
                                        found_it = True                           
                            
                            # check for artist match
                            if artist.upper() != split_array[4].upper():
                                # cycle through till will hit the right artist
                                found_it = False
                                for x in range(1, len(query_results) - 1):
                                    y = query_results[x].split('; ')
                                    #print y
                                    if (y[4].upper() == artist.upper()) & (found_it != True):
                                        song_id = y[1]
                                        self.parent.lc_playlist.SetStringItem(playlist_number, 3, song_id)
                                        self.parent.SavePlaylist(self.parent.main_playlist_location)
                                        found_it = True
                                if found_it == False:
                                    self.parent.lc_playlist.SetItemBackgroundColour(playlist_number, lolight)                    
                                    # don't scrobb the wrong song
                                    self.parent.scrobbed_track = 1
                                    self.parent.lc_playlist.SetStringItem(playlist_number, 3, song_id)
                            #update playlist
                            else:
                                self.parent.lc_playlist.SetStringItem(playlist_number, 3, song_id)
                                self.parent.SavePlaylist(self.parent.main_playlist_location)
                        else:
                            # we fucked
                            #print "no search results -- fucked"
                            pass
"""