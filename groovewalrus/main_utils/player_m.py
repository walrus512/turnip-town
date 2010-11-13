# -*- coding: utf-8 -*-
"""
GrooveWalrus: mplayer
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
import main_thirdp.mpylayer as mpylayer

########################################################################
class Player(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parent):
       
        self.parent = parent
        try:
            self.mediaPlayer = mpylayer.MPlayerControl()
        except Exception, expt:
            print u"player_m: " + str(Exception) + str(expt)
        self.paused = False        
        
    #----------------------------------------------------------------------
        
    def Play(self, file_name):
        self.mediaPlayer.loadfile(file_name)
        self.SetParentVolume()
        
    def Stop(self):        
        try:
            self.mediaPlayer.stop()
        except Exception, expt:
            print u"player_m: " + str(Exception) + str(expt)
    
    def SetVolume(self, volume):        
        try:
            self.mediaPlayer.volume = volume
        except Exception, expt:
            print u"player_m: " + str(Exception) + str(expt)
        
    def SetParentVolume(self):
        # get the current volume level
        self.SetVolume(self.parent.GetVolume())
        
    def stop_play(self):
        self.mediaPlayer.stop()
                
    def TogglePause(self, status):
        if status == 'paused':
            self.mediaPlayer.pause()
            self.paused = True
        else:
            self.mediaPlayer.pause()
            self.paused = False

        
