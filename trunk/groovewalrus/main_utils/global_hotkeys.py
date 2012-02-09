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
from main_utils import options
from main_utils import system_files
    
class GlobalHotkeys():
    def __init__(self, parent):
        self.parent = parent
        # defaults
        # prev / play(pause) / stop / next
        self.GetSavedHotkeys()
        parent.Bind(wx.EVT_HOTKEY, self.SetGlobalHotkey, id=100, id2=108)

    def SetGlobalHotkey(self, event):
        keyp = event.GetId()
        if keyp == 100:
            self.parent.OnBackwardClick(event=None)
        elif keyp == 101:
            self.parent.OnPlayClick(event=None)
        elif keyp == 102:
            self.parent.OnStopClick(event=None)
        elif keyp == 103:
            self.parent.OnForwardClick(event=None)
        elif keyp == 104:
            self.parent.OnVolumeUp(event=None)
        elif keyp == 105:
            self.parent.OnVolumeDown(event=None)
        elif keyp == 106:
            self.parent.OnMuteClick(event=None)
        elif keyp == 107:
            self.parent.OnRandomClick(event=None)
        elif keyp == 108:
            self.parent.OnRepeatClick(event=None)
            
    def GetSavedHotkeys(self):
        #grabbed the saved keys from the settings db, or not
        
        self.FILEDB = system_files.GetDirectories(self).DatabaseLocation()
        # hotkey-modifier, hotkey-previous, hotkey-play, hotkey-next, hotkey-stop
        hotkey_modifier = options.GetSetting('hotkey-modifier', self.FILEDB)
        if hotkey_modifier == '0':
            if os.name == 'nt':
                hotkey_modifier = win32con.MOD_CONTROL
            else:
                hotkey_modifier = wx.MOD_CONTROL
        if hotkey_modifier == '1':
            if os.name == 'nt':
                hotkey_modifier = win32con.MOD_SHIFT
            else:
                hotkey_modifier = wx.MOD_SHIFT
        if hotkey_modifier == '2':
            if os.name == 'nt':
                hotkey_modifier = win32con.MOD_WIN
            else:
                hotkey_modifier = wx.MOD_WIN
                 
        h1 = options.GetSetting('hotkey-previous', self.FILEDB)
        h2 = options.GetSetting('hotkey-play', self.FILEDB)
        h3 = options.GetSetting('hotkey-stop', self.FILEDB)
        h4 = options.GetSetting('hotkey-next', self.FILEDB)
        h5 = options.GetSetting('hotkey-volume-down', self.FILEDB)
        h6 = options.GetSetting('hotkey-volume-up', self.FILEDB)
        h7 = options.GetSetting('hotkey-volume-mute', self.FILEDB)
        h8 = options.GetSetting('hotkey-shuffle', self.FILEDB)
        h9 = options.GetSetting('hotkey-repeat', self.FILEDB)
        
        if (hotkey_modifier == False) & (h1 == False):
            #use defaults
            if os.name == 'nt':
                modc = win32con.MOD_CONTROL
                h1 = win32con.VK_F1
                h2 = win32con.VK_F2
                h3 = win32con.VK_F3
                h4 = win32con.VK_F4
                h5 = win32con.VK_F5
                h6 = win32con.VK_F6
                h7 = win32con.VK_F7
                h8 = win32con.VK_F9
                h9 = win32con.VK_F10
            else:
                modc = wx.MOD_CONTROL
                h1 = wx.WXK_F1
                h2 = wx.WXK_F2
                h3 = wx.WXK_F3
                h4 = wx.WXK_F4
                h5 = wx.WXK_F5
                h6 = wx.WXK_F6
                h7 = wx.WXK_F7
                h8 = wx.WXK_F9
                h9 = wx.WXK_F10
                
            self.RegisterHotkeys(str(modc), h1, h2, h3, h4, h5, h6, h7, h8, h9)
        else:
            #use stored values
            self.RegisterHotkeys(hotkey_modifier, h1, h2, h3, h4, h5, h6, h7, h8, h9)
        
    def RegisterHotkeys(self, modc, h1, h2, h3, h4, h5, h6, h7, h8, h9):
        #assign the keys
        the_keys = [h1, h2, h3, h4, h5, h6, h7, h8, h9]
        mod_type = options.GetSetting('hotkey-modifier-type', self.FILEDB)
        if (mod_type == '1'):
            counter  = 100
            for x in the_keys:
                try:
                    self.parent.RegisterHotKey(counter, 0, int(x))
                except Exception, expt:
                    print str(Exception) + str(expt)
                counter = counter + 1
            #self.parent.RegisterHotKey(100, 0, int(h1))
            #self.parent.RegisterHotKey(101, 0, int(h2))
            #self.parent.RegisterHotKey(102, 0, int(h3))
            #self.parent.RegisterHotKey(103, 0, int(h4))
            #self.parent.RegisterHotKey(104, 0, int(h5))
            #self.parent.RegisterHotKey(105, 0, int(h6))
            #self.parent.RegisterHotKey(106, 0, int(h7))
            #self.parent.RegisterHotKey(107, 0, int(h8))
            #self.parent.RegisterHotKey(108, 0, int(h9))            
        elif mod_type == '0':
            counter  = 100
            for x in the_keys:
                try:
                    self.parent.RegisterHotKey(counter, int(modc), int(x))
                except Exception, expt:
                    print str(Exception) + str(expt)
                counter = counter + 1
            #self.parent.RegisterHotKey(100, int(modc), int(h1))
            #self.parent.RegisterHotKey(101, int(modc), int(h2))
            #self.parent.RegisterHotKey(102, int(modc), int(h3))
            #self.parent.RegisterHotKey(103, int(modc), int(h4))
            #self.parent.RegisterHotKey(104, int(modc), int(h5))
            #self.parent.RegisterHotKey(105, int(modc), int(h6))
            #self.parent.RegisterHotKey(106, int(modc), int(h7))
            #self.parent.RegisterHotKey(107, int(modc), int(h8))
            #self.parent.RegisterHotKey(108, int(modc), int(h9))
            