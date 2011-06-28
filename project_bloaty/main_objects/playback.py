# -*- coding: utf-8 -*-
"""
GrooveWalrus: playback
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

#loads backend
#controls playback
import backend

########################################################################
class Playback:
    """It's a playback"""
    #----------------------------------------------------------------------
    def __init__(self, song=None):
        #set backend
        be = backend.Backend()
        bl = be.GetBackendList()
        self.player = be.SetBackend(bl[0])
        self.song = song
        #self.player = backend.player.Player()
        self.is_playing = False
        self.is_plaused = False
        self.playback_modes = ['normal', 'repeat', 'repeat all', 'random']
        self.playback_mode = self.playback_modes[0]
        
    #----------------------------------------------------------------------
        
    def Play(self, song):
        #title, artist, time, album, location
        #song.file_name = 'asfasf'
        self.player.Play(song)
        
    def Stop(self):
        '''Stop playback'''
        self.player.Stop()
        
    def Next(self):
        ''' Play next track '''
        pass
    
    def Previous(self):
        '''Play previous track'''
        pass
   
    def SeekForward(self):
        '''Seek foward in current track'''
        pass
    
    def SeekBackward(self):
        '''Seek backward in current track'''
        pass
        

if __name__ == "__main__":       
    x = Playback('poop')
    x.Play('pop')
    x.Stop()
    print x.playback_mode