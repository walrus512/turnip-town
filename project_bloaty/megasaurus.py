# -*- coding: utf-8 -*-
"""
GrooveWalrus: megasaurus
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

#megasaurus - combines all the junk into a mega class for including in the xml-rpc server

from main_objects import playlist
from main_objects import playback
from main_objects import backend

########################################################################
class Megasaurus(playlist.Playlist, playback.Playback, backend.Backend):
    """It's a playlist"""
    #----------------------------------------------------------------------
    def __init__(self, playlist_name=None):
        self.playlist = []
        self.name = playlist_name
        self.current_song = -1
    #----------------------------------------------------------------------
    # playlists ----------- 
    def CreatePlaylist(self):
        '''Creates a new playlist'''
        pass
        
    # playback -----------
    
    
    # backends -----------
    
    
    # settings -----------
        