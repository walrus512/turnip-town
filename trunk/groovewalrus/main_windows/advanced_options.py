# -*- coding: utf-8 -*-
"""
GrooveWalrus: Advanced Options
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
#After adding directories which contain your mp3 files to your song collection (may take some time depending on number of files), the directories will be monitored and updated as new mp3's are added.

import wx
import wx.xrc as xrc
import os, sys
from main_utils import system_files
from main_windows import options_window

SYSLOC = os.path.abspath(os.path.dirname(sys.argv[0]))
if os.path.isfile(SYSLOC + os.sep + "layout.xml") == False:
    SYSLOC = os.path.abspath(os.getcwd())
    
SONGDB_RESFILE = SYSLOC + os.sep + 'layout_advanced_options.xml'
#GRAPHICS_LOCATION = os.path.join(os.getcwd(), 'graphics') + os.sep

class AdvancedOptionsWindow(wx.Dialog):
    """Advacned Options Window for viewing/modifying options"""
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, "Advanced Options", size=(600, 400), pos=(10,10))#, style=wx.FRAME_SHAPED) #STAY_ON_TOP)#wx.FRAME_SHAPED)
        self.parent = parent
        
        self.FILEDB = system_files.GetDirectories(None).DatabaseLocation()
        
        # XML Resources can be loaded from a file like this:
        res = xrc.XmlResource(SONGDB_RESFILE)

        # Now create a panel from the resource data
        panel = res.LoadPanel(self, "m_pa_advanced_options")

        # control references --------------------
        self.lc_advanced_options = xrc.XRCCTRL(self, 'm_lc_advanced_options')
        #self.tc_option_value = xrc.XRCCTRL(self, 'm_tc_option_value')
        #self.st_option_name = xrc.XRCCTRL(self, 'm_st_option_name')
        self.tc_new_name = xrc.XRCCTRL(self, 'm_tc_new_name')
        self.tc_new_value = xrc.XRCCTRL(self, 'm_tc_new_value')
        
        self.lc_advanced_options.InsertColumn(0,"Option Name")
        self.lc_advanced_options.InsertColumn(1,"Option Value")
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.DisplayOption, self.lc_advanced_options)
        
        # bindings ----------------
        #self.Bind(wx.EVT_BUTTON, self.OnUpdateOption, id=xrc.XRCID('m_bu_update_option'))
        self.Bind(wx.EVT_BUTTON, self.OnAddOption, id=xrc.XRCID('m_bu_add_option'))
            
        # set layout --------------
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel, 1, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        
        self.DisplayAllOptions()        
       
#----------------------------------------------------------------------
    def ShowMe(self):
        # show the window
        #self.MoveMe()
        self.Show(True) # Shows it    
        
    def MoveMe(self, event=None):
        # show the window        
        ps = self.parent.GetSize()
        pp = self.parent.GetScreenPosition()
        ss = self.GetSize()        
        xn = pp[0] + (ps[0] - ss[0])
        yn = pp[1] + (ps[1] - ss[1])
        #self.SetSize((450, 450))
        self.SetPosition((xn, yn))        
        
    def HideMe(self, event=None):
        # hide the window
        self.Show(False)
        
    def OnExitClick(self, event):
        self.Destroy()
    
# --------------------------------------------------------- 
    def DisplayOption(self, event):
        val = self.lc_advanced_options.GetFirstSelected()
        option_name = self.lc_advanced_options.GetItem(val, 0).GetText()
        option_value = self.lc_advanced_options.GetItem(val, 1).GetText()
        #set new value        
        self.tc_new_name.SetLabel(option_name)
        self.tc_new_value.SetValue(option_value)
        
    def OnUpdateOption(self, event):
        print 'frrf'
        
    def OnAddOption(self, event):
        setting_name = self.tc_new_name.GetLabel()
        setting_value = self.tc_new_value.GetValue()
        if len(setting_name) >= 1:
            options_window.SetSetting(setting_name, setting_value, self.FILEDB)
            self.lc_advanced_options.DeleteAllItems()
            self.DisplayAllOptions()
        
    def DisplayAllOptions(self):
        """ Loads all the options and display on the list control. """
        all_options = options_window.GetAllSettings(self.FILEDB)
        counter = 0
        for x in all_options:
            self.lc_advanced_options.InsertStringItem(counter, x[1])
            self.lc_advanced_options.SetStringItem(counter, 1, x[2])
            counter = counter + 1
        self.lc_advanced_options.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.lc_advanced_options.SetColumnWidth(1, wx.LIST_AUTOSIZE)