# -*- coding: utf-8 -*-
"""
GrooveWalrus: pyglet player
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

import pyglet
from threading import Thread

pyglet.options['audio'] = ('directsound', 'alsa', 'openal', 'silent')

########################################################################
class Player(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parent):
       
        self.parent = parent        
        self.paused = False
        self.play_thread = None
     
    #----------------------------------------------------------------------
        
    def Play(self, file_name):
        #print file_name
        self.mediaPlayer = pyglet.media.Player()
        source = pyglet.media.load(file_name)
        self.mediaPlayer.queue(source)
        #self.mediaPlayer.next(source)
        self.play_thread = PlayThread(self)
        #THREAD
        self.play_thread.start()

    def Stop(self):
        if self.play_thread != None:
            self.play_thread.stop()
            
    def SetVolume(self, volume):
        pass
        
    def stop_play(self):
        self.mediaPlayer.stop()
                
    def TogglePause(self, status):
        if self.mediaPlayer.playing:
            self.mediaPlayer.pause()
        else:
            if self.mediaPlayer.time >= self.mediaPlayer.source.duration:
                self.mediaPlayer.seek(0)
            self.mediaPlayer.play()

class PlayThread(Thread):
    """ makes a thread for pyglet playback """
    def __init__(self, parent):
        Thread.__init__(self)
        self.paused = False
        self.parent = parent
        
    def run(self):
        while self.paused != True:
            self.parent.mediaPlayer.play()
            
    def pause(self):
        self.paused = True
        
    def stop(self):
        self.paused = True
        #if self.parent.mediaPlayer != None:
        self.parent.mediaPlayer.pause()    
        #    self.parent.mediaPlayer = None