#!/bin/env python
"""
GrooveWalrus: Global Hotkeys
Copyright (C) 2009
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
import os
if os.name == 'nt':
    import win32con
from main_windows import options_window
from main_utils import system_files
    
class GlobalHotkeys():
    def __init__(self, parent):
        self.parent = parent
        # defaults
        # prev / play(pause) / stop / next
        self.GetSavedHotkeys()
        parent.Bind(wx.EVT_HOTKEY, self.SetGlobalHotkey, id=100, id2=103)

    def SetGlobalHotkey(self, event):
        keyp = event.GetId()
        if keyp == 100:
            self.parent.OnBackwardClick(event=None)
        elif keyp == 101:
            self.parent.OnPlayClick(event=None)
        elif keyp == 103:
            self.parent.OnForwardClick(event=None)
        else:
            self.parent.OnStopClick(event=None)
            
    def GetSavedHotkeys(self):
        #grabbed the saved keys from the settings db, or not
        
        self.FILEDB = system_files.GetDirectories(self).DatabaseLocation()
        # hotkey-modifier, hotkey-previous, hotkey-play, hotkey-next, hotkey-stop
        hotkey_modifier = options_window.GetSetting('hotkey-modifier', self.FILEDB)
        hotkey_previous = options_window.GetSetting('hotkey-previous', self.FILEDB)
        hotkey_play = options_window.GetSetting('hotkey-play', self.FILEDB)
        hotkey_next = options_window.GetSetting('hotkey-next', self.FILEDB)
        hotkey_stop = options_window.GetSetting('hotkey-stop', self.FILEDB)
        
        if (hotkey_modifier == False) & (hotkey_play == False):
            #use defaults
            if os.name == 'nt':
                modc = win32con.MOD_CONTROL
                h1 = win32con.VK_F1
                h2 = win32con.VK_F2
                h3 = win32con.VK_F3
                h4 = win32con.VK_F4                
            else:
                modc = wx.MOD_CONTROL
                h1 = wx.WXK_F1
                h2 = wx.WXK_F2
                h3 = wx.WXK_F3
                h4 = wx.WXK_F4                
                
            self.RegisterHotkeys(str(modc), h1, h2, h3, h4)
        else:
            #use stored values
            self.RegisterHotkeys(hotkey_modifier, hotkey_previous, hotkey_play, hotkey_stop, hotkey_next)
        
    def RegisterHotkeys(self, modc, h1, h2, h3, h4):
        #assign the keys
        if (modc == False) | (modc == 0):
            self.parent.RegisterHotKey(100, int(h1))
            self.parent.RegisterHotKey(101, int(h2))
            self.parent.RegisterHotKey(102, int(h3))
            self.parent.RegisterHotKey(103, int(h4))
        else:
            self.parent.RegisterHotKey(100, eval(modc), int(h1))
            self.parent.RegisterHotKey(101, eval(modc), int(h2))
            self.parent.RegisterHotKey(102, eval(modc), int(h3))
            self.parent.RegisterHotKey(103, eval(modc), int(h4))