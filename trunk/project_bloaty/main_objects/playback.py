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
import os

########################################################################
class Playback:
    """It's a playback"""
    #----------------------------------------------------------------------
    def __init__(self, song=None):
        #set backend
        bl = backend.Backend().GetBackendList()
        self.PlaybackSetBackend(bl[0])
        #self.player = be.SetBackend(bl[0])
        self.song = song
        #self.player = backend.player.Player()
        self.is_playing = False
        self.is_plaused = False
        self.playback_modes = ['normal', 'repeat', 'repeat_all', 'random']
        self.playback_mode = self.playback_modes[0]
        
    #----------------------------------------------------------------------
    def PlaybackSetBackend(self, this_backend):
        return backend.Backend().SetBackend(this_backend)
        
    def Play(self, item):
        #title, artist, time, album, location
        #song.file_name = 'asfasf'        
        self.player.Play(item.location)
        
    def PlayWith(self, this_backend, location):
        print location
        self.player = self.PlaybackSetBackend(this_backend)
        #self.player = backend.Backend().SetBackend(this_backend)
        self.Stop()        
        
        #check file exists
        if os.path.isfile(location): 
            self.player.Play(location)
        else:
            pass
        #check local
        #check cache
        #check online (grooveshark)
        
        
    def Stop(self):
        '''Stop playback'''
        print self.player
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