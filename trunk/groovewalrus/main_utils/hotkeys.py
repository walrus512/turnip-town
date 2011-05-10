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
        h5 = options_window.GetSetting('acc-volume-up', self.FILEDB)
        if h5: 
            h5 = int(h5)
        else: 
            h5 = wx.WXK_F6
        h6 = options_window.GetSetting('acc-volume-down', self.FILEDB)
        if h6: 
            h6 = int(h6)
        else: 
            h6 = wx.WXK_F5
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
                                   (wx.ACCEL_NORMAL, h8, randID),
                                   (wx.ACCEL_NORMAL, h9, reapID),
                                   (wx.ACCEL_NORMAL, h6, vldnID),
                                   (wx.ACCEL_NORMAL, h5, vlupID),
                                   (wx.ACCEL_NORMAL, h7, muteID),
                                   #(wx.ACCEL_CTRL, ord('.'), ctrlperiodID)
                                   ]
                                           
                                           
        aTable = wx.AcceleratorTable(self.parent.aTable_values)
        #add to main program
        self.parent.SetAcceleratorTable(aTable)
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