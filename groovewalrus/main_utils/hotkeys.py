#!/bin/env python
"""
GrooveWalrus: Global Hotkeys
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

import wx
from main_windows import options_window
from main_utils import system_files
    
keyMap = {
    wx.WXK_BACK : "BACK",
    wx.WXK_TAB : "TAB",
    wx.WXK_RETURN : "RETURN",
    wx.WXK_ESCAPE : "ESCAPE",
    wx.WXK_SPACE : "SPACE",
    wx.WXK_DELETE : "DELETE",
    wx.WXK_START : "START",
    wx.WXK_LBUTTON : "LBUTTON",
    wx.WXK_RBUTTON : "RBUTTON",
    wx.WXK_CANCEL : "CANCEL",
    wx.WXK_MBUTTON : "MBUTTON",
    wx.WXK_CLEAR : "CLEAR",
    wx.WXK_SHIFT : "SHIFT",
    wx.WXK_ALT : "ALT",
    wx.WXK_CONTROL : "CONTROL",
    wx.WXK_MENU : "MENU",
    wx.WXK_PAUSE : "PAUSE",
    wx.WXK_CAPITAL : "CAPITAL",
    #wx.WXK_PRIOR : "PRIOR",
    #wx.WXK_NEXT : "NEXT",
    wx.WXK_END : "END",
    wx.WXK_HOME : "HOME",
    wx.WXK_LEFT : "LEFT",
    wx.WXK_UP : "UP",
    wx.WXK_RIGHT : "RIGHT",
    wx.WXK_DOWN : "DOWN",
    wx.WXK_SELECT : "SELECT",
    wx.WXK_PRINT : "PRINT",
    wx.WXK_EXECUTE : "EXECUTE",
    wx.WXK_SNAPSHOT : "SNAPSHOT",
    wx.WXK_INSERT : "INSERT",
    wx.WXK_HELP : "HELP",
    wx.WXK_NUMPAD0 : "NUMPAD0",
    wx.WXK_NUMPAD1 : "NUMPAD1",
    wx.WXK_NUMPAD2 : "NUMPAD2",
    wx.WXK_NUMPAD3 : "NUMPAD3",
    wx.WXK_NUMPAD4 : "NUMPAD4",
    wx.WXK_NUMPAD5 : "NUMPAD5",
    wx.WXK_NUMPAD6 : "NUMPAD6",
    wx.WXK_NUMPAD7 : "NUMPAD7",
    wx.WXK_NUMPAD8 : "NUMPAD8",
    wx.WXK_NUMPAD9 : "NUMPAD9",
    wx.WXK_MULTIPLY : "MULTIPLY",
    wx.WXK_ADD : "ADD",
    wx.WXK_SEPARATOR : "SEPARATOR",
    wx.WXK_SUBTRACT : "SUBTRACT",
    wx.WXK_DECIMAL : "DECIMAL",
    wx.WXK_DIVIDE : "DIVIDE",
    wx.WXK_F1 : "F1",
    wx.WXK_F2 : "F2",
    wx.WXK_F3 : "F3",
    wx.WXK_F4 : "F4",
    wx.WXK_F5 : "F5",
    wx.WXK_F6 : "F6",
    wx.WXK_F7 : "F7",
    wx.WXK_F8 : "F8",
    wx.WXK_F9 : "F9",
    wx.WXK_F10 : "F10",
    wx.WXK_F11 : "F11",
    wx.WXK_F12 : "F12",
    wx.WXK_F13 : "F13",
    wx.WXK_F14 : "F14",
    wx.WXK_F15 : "F15",
    wx.WXK_F16 : "F16",
    wx.WXK_F17 : "F17",
    wx.WXK_F18 : "F18",
    wx.WXK_F19 : "F19",
    wx.WXK_F20 : "F20",
    wx.WXK_F21 : "F21",
    wx.WXK_F22 : "F22",
    wx.WXK_F23 : "F23",
    wx.WXK_F24 : "F24",
    wx.WXK_NUMLOCK : "NUMLOCK",
    wx.WXK_SCROLL : "SCROLL",
    wx.WXK_PAGEUP : "PAGEUP",
    wx.WXK_PAGEDOWN : "PAGEDOWN",
    wx.WXK_NUMPAD_SPACE : "NUMPAD_SPACE",
    wx.WXK_NUMPAD_TAB : "NUMPAD_TAB",
    wx.WXK_NUMPAD_ENTER : "NUMPAD_ENTER",
    wx.WXK_NUMPAD_F1 : "NUMPAD_F1",
    wx.WXK_NUMPAD_F2 : "NUMPAD_F2",
    wx.WXK_NUMPAD_F3 : "NUMPAD_F3",
    wx.WXK_NUMPAD_F4 : "NUMPAD_F4",
    wx.WXK_NUMPAD_HOME : "NUMPAD_HOME",
    wx.WXK_NUMPAD_LEFT : "NUMPAD_LEFT",
    wx.WXK_NUMPAD_UP : "NUMPAD_UP",
    wx.WXK_NUMPAD_RIGHT : "NUMPAD_RIGHT",
    wx.WXK_NUMPAD_DOWN : "NUMPAD_DOWN",
    #wx.WXK_NUMPAD_PRIOR : "NUMPAD_PRIOR",
    wx.WXK_NUMPAD_PAGEUP : "NUMPAD_PAGEUP",
    #wx.WXK_NUMPAD_NEXT : "NUMPAD_NEXT",
    wx.WXK_NUMPAD_PAGEDOWN : "NUMPAD_PAGEDOWN",
    wx.WXK_NUMPAD_END : "NUMPAD_END",
    wx.WXK_NUMPAD_BEGIN : "NUMPAD_BEGIN",
    wx.WXK_NUMPAD_INSERT : "NUMPAD_INSERT",
    wx.WXK_NUMPAD_DELETE : "NUMPAD_DELETE",
    wx.WXK_NUMPAD_EQUAL : "NUMPAD_EQUAL",
    wx.WXK_NUMPAD_MULTIPLY : "NUMPAD_MULTIPLY",
    wx.WXK_NUMPAD_ADD : "NUMPAD_ADD",
    wx.WXK_NUMPAD_SEPARATOR : "NUMPAD_SEPARATOR",
    wx.WXK_NUMPAD_SUBTRACT : "NUMPAD_SUBTRACT",
    wx.WXK_NUMPAD_DECIMAL : "NUMPAD_DECIMAL",
    wx.WXK_NUMPAD_DIVIDE : "NUMPAD_DIVIDE",

    wx.WXK_WINDOWS_LEFT : "WINDOWS_LEFT",
    wx.WXK_WINDOWS_RIGHT : "WINDOWS_RIGHT",
    wx.WXK_WINDOWS_MENU : "WINDOWS_MENU",

    wx.WXK_COMMAND : "COMMAND",
    
    wx.WXK_SPECIAL1 : "SPECIAL1",
    wx.WXK_SPECIAL2 : "SPECIAL2",
    wx.WXK_SPECIAL3 : "SPECIAL3",
    wx.WXK_SPECIAL4 : "SPECIAL4",
    wx.WXK_SPECIAL5 : "SPECIAL5",
    wx.WXK_SPECIAL6 : "SPECIAL6",
    wx.WXK_SPECIAL7 : "SPECIAL7",
    wx.WXK_SPECIAL8 : "SPECIAL8",
    wx.WXK_SPECIAL9 : "SPECIAL9",
    wx.WXK_SPECIAL10 : "SPECIAL10",
    wx.WXK_SPECIAL11 : "SPECIAL11",
    wx.WXK_SPECIAL12 : "SPECIAL12",
    wx.WXK_SPECIAL13 : "SPECIAL13",
    wx.WXK_SPECIAL14 : "SPECIAL14",
    wx.WXK_SPECIAL15 : "SPECIAL15",
    wx.WXK_SPECIAL16 : "SPECIAL16",
    wx.WXK_SPECIAL17 : "SPECIAL17",
    wx.WXK_SPECIAL18 : "SPECIAL18",
    wx.WXK_SPECIAL19 : "SPECIAL19",
    wx.WXK_SPECIAL20 : "SPECIAL20",
}

class Hotkeys():
    def __init__(self, parent):
        self.parent = parent
        
    def SetHotkeys(self):    
        backID = 701
        playID = 702
        stopID = 703
        forwID = 704
        #saveID = 705
        #loadID = 706
        randID = 707
        reapID = 708
        vlupID = 709
        vldnID = 7010
        #tbupID = 7012
        muteID = 7011
        #tbdnID = 7011
        #ctrldID = 801
        #ctrlrID = 802
        #ctrlbID = 803
        #ctrl9ID = 910
        #ctrl8ID = 911
        #ctrlfID = 804
        #ctrlmID = 805        
        #ctrlgID = 806
        #ctrlperiodID = 807
        
        self.FILEDB = system_files.GetDirectories(self).DatabaseLocation()
        
        
        
        h1 = options_window.GetSetting('acc-previous', self.FILEDB)
        if h1: 
            h1 = int(h1)
        else: 
            h1 = wx.WXK_F1
            
        h2 = options_window.GetSetting('acc-play', self.FILEDB)
        if h2: 
            h2 = int(h2)
        else: 
            h2 = wx.WXK_F2
            
        h3 = options_window.GetSetting('acc-stop', self.FILEDB)
        if h3: 
            h3 = int(h3)
        else: 
            h3 = wx.WXK_F3
            
        h4 = options_window.GetSetting('acc-next', self.FILEDB)
        if h4: 
            h4 = int(h4)
        else: 
            h4 = wx.WXK_F4
            
        h5 = options_window.GetSetting('acc-volume-down', self.FILEDB)
        if h5: 
            h5 = int(h5)
        else: 
            h5 = wx.WXK_F5
            
        h6 = options_window.GetSetting('acc-volume-up', self.FILEDB)
        if h6: 
            h6 = int(h6)
        else: 
            h6 = wx.WXK_F6
            
        h7 = options_window.GetSetting('acc-volume-mute', self.FILEDB)
        if h7: 
            h7 = int(h7)
        else: 
            h7 = wx.WXK_F7
            
        h8 = options_window.GetSetting('acc-shuffle', self.FILEDB)
        if h8: 
            h8 = int(h8)
        else: 
            h8 = wx.WXK_F9
            
        h9 = options_window.GetSetting('acc-repeat', self.FILEDB)
        if h9: 
            h9 = int(h9)
        else: 
            h9 = wx.WXK_F10
        
        #clear acc table
        aTable = wx.NullAcceleratorTable
        self.parent.SetAcceleratorTable(aTable)
        self.parent.album_viewer.SetAcceleratorTable(aTable)
        
        self.parent.aTable_values = [
                                   (wx.ACCEL_NORMAL, h1, backID),
                                   (wx.ACCEL_NORMAL, h2, playID),
                                   (wx.ACCEL_NORMAL, h3, stopID),
                                   (wx.ACCEL_NORMAL, h4, forwID),
                                   (wx.ACCEL_NORMAL, h5, vldnID),
                                   (wx.ACCEL_NORMAL, h6, vlupID),
                                   (wx.ACCEL_NORMAL, h7, muteID),
                                   (wx.ACCEL_NORMAL, h8, randID),
                                   (wx.ACCEL_NORMAL, h9, reapID),

                                   #(wx.ACCEL_CTRL, ord('.'), ctrlperiodID)
                                   ]
                                           
        ###self.SetMenuAccel(h1, backID)
        counter = 0
        for menu_item in self.parent.parent.menu_playback.GetMenuItems():
            #print menu_item
            self.SetMenuAccel(menu_item, self.parent.aTable_values[counter][1], self.parent.aTable_values[counter][2])
            counter = counter + 1
        
        aTable = wx.AcceleratorTable(self.parent.aTable_values)
        #add to main program
        ####self.parent.SetAcceleratorTable(aTable)
        #add to album viewer window too
        self.parent.album_viewer.SetAcceleratorTable(aTable)
         
        wx.EVT_MENU(self.parent, backID, self.parent.OnBackwardClick)
        wx.EVT_MENU(self.parent, playID, self.parent.OnPlayClick)
        wx.EVT_MENU(self.parent, stopID, self.parent.OnStopClick)
        wx.EVT_MENU(self.parent, forwID, self.parent.OnForwardClick) 
        
        #wx.EVT_MENU(self, saveID, self.OnSavePlaylistClick)
        #wx.EVT_MENU(self, loadID, self.OnLoadPlaylistClick)
        wx.EVT_MENU(self.parent, randID, self.parent.OnRandomClick)
        wx.EVT_MENU(self.parent, reapID, self.parent.OnRepeatClick)
        
        wx.EVT_MENU(self.parent, vldnID, self.parent.OnVolumeDown)
        wx.EVT_MENU(self.parent, vlupID, self.parent.OnVolumeUp)
        wx.EVT_MENU(self.parent, muteID, self.parent.OnMuteClick)
        #wx.EVT_MENU(self, tbupID, self.OnNextTab)
        
        #wx.EVT_MENU(self.parent, ctrldID, self.parent.OnClearPlaylistClick)
        #wx.EVT_MENU(self.parent, ctrlrID, self.parent.ResetPosition)
        #wx.EVT_MENU(self.parent, ctrlbID, self.parent.RandomBackgroundColour)
        #wx.EVT_MENU(self.parent, ctrlfID, self.parent.OnSearchClick)
        
        #wx.EVT_MENU(self.parent, ctrl9ID, self.parent.ClearAlbumValues)
        #wx.EVT_MENU(self.parent, ctrl8ID, self.parent.ClearIdValues)
        #wx.EVT_MENU(self.parent, ctrlmID, self.parent.MiniMode)
        #wx.EVT_MENU(self.parent, ctrlgID, self.parent.OnLoadBackgroundImage)
        #wx.EVT_MENU(self.parent, ctrlperiodID, self.parent.OnLoadAdvancedOptions)
                
    def SetMenuAccel(self, the_item, the_key, the_id):
        #wx.MenuItem.SetAccel(
        #print GetKeyName(the_key)
        try:
            the_item.SetAccel(wx.AcceleratorEntry(wx.ACCEL_NORMAL, the_key, the_id))
        except Exception, expt:
            print 'hotkeys:' + str(Exception) + str(expt)
        
def GetKeyName(keycode):
    #return a text value for a key code
    keyname = keyMap.get(keycode, None)

    if keyname is None:
        if keycode < 256:
            if keycode == 0:
                keyname = "NUL"
            elif keycode < 27:
                keyname = "Ctrl-%s" % chr(ord('A') + keycode-1)
            else:
                keyname = "%s" % chr(keycode)
        else:
            keyname = "%s" % keycode
    return keyname