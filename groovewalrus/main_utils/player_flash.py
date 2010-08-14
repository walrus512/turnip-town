# -*- coding: utf-8 -*-
"""
GrooveWalrus: flash player
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

import wx
from wx.lib.flashwin import FlashWindow

########################################################################
class Player(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parent):
       
        self.parent = parent        
        self.mediaPlayer = FlashWindow(parent.pa_flash_player, style=wx.NO_BORDER, size=wx.Size(500,140))
        self.paused = False
        
        ##self.parent.Bind(wx.EVT_MOTION, self.OnClick, self.mediaPlayer)
        
    #----------------------------------------------------------------------
        
    def Play(self, song_url):
        #print song_url
        self.mediaPlayer.movie = song_url #self.current_song.song_url
        #self.VirtualClick()
        
    def Stop(self):
        self.mediaPlayer.movie = 'temp.swf'
    
    def SetVolume(self, volume):
        pass
                        
    def TogglePause(self, status):
        pass

