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

    def VirtualClick(self):
        print 'boo'
        print self.mediaPlayer.GetPosition()
        print self.parent.GetPosition()
        print self.parent.GetSize()
        #MouseClicker(530, 360)
        
        
        
        
        #checkEvent = wx.CommandEvent(wx.wxEVT_COMMAND_RIGHT_CLICK, self.mediaPlayer.GetId())
        ##checkEvent = wx.CommandEvent(wx.wxEVT_MOTION, self.mediaPlayer.GetId())
        # checkEvent.SetInt(int(self._checked))
        ##checkEvent.SetEventObject(self.mediaPlayer)
        #checkEvent.SetPosition((10,10))
        #checkEvent.
    
        # Watch for a possible listener of this event that will catch it and
        # eventually process it


        
#        self.parent.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnClick, self.mediaPlayer)
        ##self.mediaPlayer.GetEventHandler().ProcessEvent(checkEvent)
        #instance.GetEventHandler().ProcessEvent(event) 
        #print checkEvent
        #print checkEvent.GetEventHandler()   
        
    def OnClick(self, event):
        print 'foo'
        print event
        #print 'pos: ' + str(event.GetPosition())
        
             
#import win32api
#import win32con
#win32api.keybd_event(win32con.VK_F3, 0) # this will press F3 key

#def MouseClicker(position_x, position_y):

 #   print win32api.GetFocus() # this will return you the handle of the window which has focus

  #  win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 20, 20, 0, 0) # this will press mouse left button
    #win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 20, 20, 0, 0) # this will raise mouse left button
    #win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 20, 20, 0, 0) # this will raise mouse left button
    #win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, position_x, position_y) # this will press mouse left button
    #win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, position_x, position_y) # this will press mouse left button
   # print "clicky"
    #win32api.mouse_event(win32con.MOUSEEVENTF_LEFTTUP, 0, 0) # this will raise mouse left button
    #win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0) # this will press mouse right button
    #win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0) # this will raise mouse right button
