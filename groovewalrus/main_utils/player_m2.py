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
import MplayerCtrl as mpc

########################################################################
class Player(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parent):
       
        self.parent = parent
        #self.mediaPlayer = self.parent.mediaPlayer
        #backend = eval('wx.media.MEDIABACKEND_' + self.parent.ch_options_wxbackend.GetStringSelection())
        mplayer_path = 'f:/temp/mplayer/mplayer.exe'
        self.mediaPlayer = mpc.MplayerCtrl(self.parent, -1, mplayer_path)
        self.mediaPlayer.Start()
        #self.Bind(mpc.EVT_MEDIA_STARTED, self.on_media_started)
        #self.Bind(mpc.EVT_MEDIA_FINISHED, self.on_media_finished)
        #self.Bind(mpc.EVT_PROCESS_STARTED, self.on_process_started)
        #self.Bind(mpc.EVT_PROCESS_STOPPED, self.on_process_stopped)
        
        self.paused = False        
        
    #----------------------------------------------------------------------
                  
    #def PlayWxMedia(self, event):
        #self.mediaPlayer.Play()
        
    def Play(self, file_name):
        print file_name
        #***
        self.mediaPlayer.Loadfile('"' + file_name.replace('\\', '/') + '"')
        #print self.mediaPlayer.GetFileName()
        self.SetParentVolume()
        
    def Stop(self):
        self.mediaPlayer.Stop()
    
    def SetVolume(self, volume):
        self.mediaPlayer.SetProperty("volume", volume)#float(volume)/100)
        
    def SetParentVolume(self):
        # get the current volume level
        self.SetVolume(self.parent.GetVolume())
        
    def stop_play(self):
        self.mediaPlayer.Stop()
                
    def TogglePause(self, status):
        if status == 'paused':
            self.mediaPlayer.Pause()
            self.paused = True
        else:
            self.mediaPlayer.Pause()
            self.paused = False

        
