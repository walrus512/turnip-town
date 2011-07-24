# -*- coding: utf-8 -*-
"""
GrooveWalrus: playlist
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
from main_objects import song

########################################################################
class Playlist:
    """It's a playlist"""
    #----------------------------------------------------------------------
    def __init__(self, playlist_name=None):
        self.playlist = []
        self.name = playlist_name
        self.current_song = -1
        
    #----------------------------------------------------------------------
        
    def AddItem(self, song_dict):
        #title, artist, time, album, location
        self.CheckItemDict(song_dict)
        self.playlist.append(song_dict)        
        
    def CheckItemDict(self, song_dict):
        #check to make sure there's a song title and artist
        if ('Title' in song_dict.keys()) & ('Artist' in song_dict.keys()):
            pass
        else:        
            raise StandardError('Invalid playlist item, song or artist not found.')        
            
    def DeleteItem(self, list_id):
        return(self.playlist.pop(list_id))
        
    def InsertItem(self, song_dict, position):
        self.CheckItemDict(song_dict)
        self.playlist.insert(position, song_dict)
        
    def MoveItem(self, list_id, position):
        x = self.DeleteItem(list_id)
        self.InsertItem(x, position)
    
    def GetName(self):
        return(self.name)
        
    def SetName(self, name):
        self.name = name
        return(self.name)
        
    def SetItemAttrib(self, list_id, attribute, value):
        x = self.playlist[list_id] 
        x[attribute] = value
        self.playlist[list_id] = x
        
    def GetCount(self):
        return (len(self.playlist))
    
    def GetCurrentNumber(self):
        if self.GetCount() > 0:
            if self.current_song == -1:
                self.current_song = 0
            elif self.GetCount() >= self.current_song:
                self.current_song = 0
            else:
                pass
        else:
            self.current_song = -1
        return self.current_song
    
    def SetCurrentNumber(self, number):
        self.current_song = number
        
    def GetNext(self):
        self.current_song  = self.current_song + 1
        return self.GetCurrentNumber()
    
    def GetPrevious(self):
        self.current_song  = self.current_song - 1
        return self.GetCurrentNumber()
    
    def GetNextRandom(self):
        pass
    
    def PrintPlaylist(self):
        print self.playlist
        
    def GetPlaylist(self):
        return self.playlist
        
    #--------
    
    def LoadPlaylist(self, list_name):
        '''load a playlist from the db'''
        pass
        
    def SavePlaylist(self):
        pass
    
    def ExportPlaylist(self, file_name):
        pass

if __name__ == "__main__":       
    x = Playlist()
    print x.GetName()
    x.AddItem({'artist':'Beck', 'title':'Sad Song'})
    x.AddItem({'artist':'U2', 'title':'Gloria'})
    print x.playlist
    x.SetItemAttrib(0, 'rating', 0)
    print x.playlist
    print x.DeleteItem(1)
    print x.playlist
    x.InsertItem({'artist':'U2', 'title':'Lemon'}, 0)
    print x.playlist
    x.MoveItem(0, 1)
    print x.playlist