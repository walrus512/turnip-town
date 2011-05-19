# -*- coding: utf-8 -*-
"""
GrooveWalrus: song
Copyright (C) 2011
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

#playlist object
#-add song
#-remove song
#-insert song
#-playlist history
#-playlist item - title, artist, time, album, location
#-playlist item data - last_played, first_played, times_played, rating

########################################################################
class Playlist:
    """It's a playlist"""
    #----------------------------------------------------------------------
    def __init__(self, playlist_name=None):
        self.playlist = []
        self.name = playlist_name
        self.current_song = -1
        
    #----------------------------------------------------------------------
        
    def AddSong(self, song_dict):
        #title, artist, time, album, location
        self.CheckSongDict(song_dict)
        self.playlist.append(song_dict)        
        
    def CheckSongDict(self, song_dict):
        #check to make sure there's a song title and artist
        if ('title' in song_dict.keys()) & ('artist' in song_dict.keys()):
            pass
        else:        
            raise StandardError('Invalid playlist item, song or artist not found.')        
            
    def DeleteSong(self, song_id):
        return(self.playlist.pop(song_id))
        
    def InsertSong(self, song_dict, position):
        self.CheckSongDict(song_dict)
        self.playlist.insert(position, song_dict)
        
    def MoveSong(self, song_id, position):
        x = self.DeleteSong(song_id)
        self.InsertSong(x, position)
    
    def GetName(self):
        return(self.name)
        
    def SetName(self, name):
        self.name = name
        return(self.name)
        
    def SetSongAttrib(self, song_id, attribute, value):
        x = self.playlist[song_id] 
        x[attribute] = value
        self.playlist[song_id] = x
        
    def GetCount(self):
        return (len(self.playlist))    

if __name__ == "__main__":       
    x = Playlist()
    print x.GetName()
    x.AddSong({'artist':'Beck', 'title':'Sad Song'})
    x.AddSong({'artist':'U2', 'title':'Gloria'})
    print x.playlist
    x.SetSongAttrib(0, 'rating', 0)
    print x.playlist
    print x.DeleteSong(1)
    print x.playlist
    x.InsertSong({'artist':'U2', 'title':'Lemon'}, 0)
    print x.playlist
    x.MoveSong(0, 1)
    print x.playlist