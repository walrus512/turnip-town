#!/bin/env python
"""
GrooveWalrus: Options Window 
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
import wx.xrc as xrc
import sys, os
from wx.lib import langlistctrl
from main_utils import system_files
from main_utils import options
from main_utils import file_cache

OP_ARR = [
    #General
    ['m_cb_add-all-clear', 0],
    ['m_cb_search-double-click', 0],
    ['m_cb_search-results-drop-id', 0],
    ['m_cb_tray-minimize', 0],
    ['m_tc_download-directory', ''],
    ['m_cb_download-autosave', 0],
    #Last.fm
    ['m_tc_lastfm-username', ''],
    ['m_tc_lastfm-password', ''],
    ['m_cb_lastfm-scrobble', 1],
    ['m_cb_lastfm-scrobble-album', 0],
    ['m_cb_lastfm-scrobble-port', 1],
    #Proxy
    ['m_tc_proxy-url', ''],
    ['m_cb_proxy-enabled', ''],
    #streaming
    ['m_cb_prefetch-songs', 1],
    ['m_sl_cache-size', 50],
    ]
                
                
SYSLOC = os.path.abspath(os.path.dirname(sys.argv[0]))
if os.path.isfile(SYSLOC + os.sep + "layout.xml") == False:
    SYSLOC = os.path.abspath(os.getcwd())
    
RESFILE = SYSLOC + os.sep + 'layout_options.xml'
GRAPHICS_LOCATION = os.path.join(os.getcwd(), 'graphics') + os.sep

class OptionsWindow(wx.Dialog):
    """Options Window for viewing/modifying options"""
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, "Options", size=(600, 500))#, pos=(10,10))#, style=wx.FRAME_SHAPED) #STAY_ON_TOP)#wx.FRAME_SHAPED)
        self.parent = parent
        
        self.FILEDB = system_files.GetDirectories(None).DatabaseLocation()
        
        # XML Resources can be loaded from a file like this:
        res = xrc.XmlResource(RESFILE)

        # Now create a panel from the resource data
        panel = res.LoadPanel(self, "m_pa_options")

        # control references --------------------
        #self.lb_options = xrc.XRCCTRL(self, 'm_lb_options')
        self.lc_advanced_options = xrc.XRCCTRL(self, 'm_lc_advanced_options')
        self.st_lastfm_status = xrc.XRCCTRL(self, 'm_st_lastfm_status')
        #self.tc_lastfm_password = xrc.XRCCTRL(self, 'm_tc_lastfm_password')
        #self.st_option_name = xrc.XRCCTRL(self, 'm_st_option_name')
        self.tc_new_name = xrc.XRCCTRL(self, 'm_tc_new_name')
        self.tc_new_value = xrc.XRCCTRL(self, 'm_tc_new_value')
        self.tc_download_directory = xrc.XRCCTRL(self, 'm_tc_download-directory')
        
        self.lc_advanced_options.InsertColumn(0,"Option Name")
        self.lc_advanced_options.InsertColumn(1,"Option Value")
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.DisplayOption, self.lc_advanced_options)
        
        # bindings ----------------
        #self.Bind(wx.EVT_BUTTON, self.OnUpdateOption, id=xrc.XRCID('m_bu_update_option'))
        self.Bind(wx.EVT_BUTTON, self.OnAddOption, id=xrc.XRCID('m_bu_add_option'))
        self.Bind(wx.EVT_BUTTON, self.OnSaveClick, id=xrc.XRCID('m_bu_ok'))
        self.Bind(wx.EVT_BUTTON, self.OnExitClick, id=xrc.XRCID('m_bu_cancel'))
        self.Bind(wx.EVT_BUTTON, self.SetLanguage, id=xrc.XRCID('m_bu_options_language'))
        self.Bind(wx.EVT_BUTTON, self.OnBrowseClick, id=xrc.XRCID('m_bu_download_browse'))
        self.Bind(wx.EVT_BUTTON, self.OnClearCacheClick, id=xrc.XRCID('m_bu_cache_clear'))
        self.Bind(wx.EVT_BUTTON, self.OnLastfmTestClick, id=xrc.XRCID('m_bu_lastfm_test'))
            
        # set layout --------------
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel, 1, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        #self.SetSize(self.GetEffectiveMinSize())
        
        self.LoadOptions()
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
        
    def OnSaveClick(self, event):
        self.SaveOptions()
        self.SetScrobbleMenuItem()
        self.OnExitClick(None)
         
    def OnExitClick(self, event):
        self.Destroy()
    
# ---------------------------------------------------------
    def LoadOptions(self):
        """ load options from file, populate options tabs """
        for x in OP_ARR:
            setting_value = options.GetSetting(x[0].rsplit('_', 1)[1], self.FILEDB)            
            if setting_value:
                try:
                    xrc.XRCCTRL(self, x[0]).SetValue(setting_value)
                except TypeError:
                    #print xrc.XRCCTRL(self, x[0])
                    if setting_value == 'False':
                        setting_value = '0'
                    if setting_value == 'True':
                        setting_value = '1'
                    xrc.XRCCTRL(self, x[0]).SetValue(int(setting_value))                    
        
    def SaveOptions(self):
        """ saves options to file """
        for x in OP_ARR:
            setting_value = xrc.XRCCTRL(self, x[0]).GetValue()
            try:
                str(setting_value)
                #print x[0]
                #print setting_value
            except Exception, e:
                print "SaveOptions: " + x[0] + str(Exception) + str(e)
                
            if setting_value != '':
                if (setting_value == 'True'):
                    setting_value = '1'
                if setting_value == 'False':
                    setting_value = '0'
                if type(setting_value) == type(True):                    
                    if setting_value == False:
                        setting_value = '0'
                    else:
                        setting_value = '1'
                options.SetSetting(x[0].rsplit('_', 1)[1], setting_value, self.FILEDB)                

# ---------------------------------------------------------
# Advanced tab
    def DisplayOption(self, event):
        val = self.lc_advanced_options.GetFirstSelected()
        option_name = self.lc_advanced_options.GetItem(val, 0).GetText()
        option_value = self.lc_advanced_options.GetItem(val, 1).GetText()
        #set new value        
        self.tc_new_name.SetLabel(option_name)
        self.tc_new_value.SetValue(option_value)
        
    def OnAddOption(self, event):
        setting_name = self.tc_new_name.GetLabel()
        setting_value = self.tc_new_value.GetValue()
        if len(setting_name) >= 1:
            options.SetSetting(setting_name, setting_value, self.FILEDB)
            self.lc_advanced_options.DeleteAllItems()
            self.DisplayAllOptions()
        
    def DisplayAllOptions(self):
        """ Loads all the options and display on the list control. """
        all_options = options.GetAllSettings(self.FILEDB)
        counter = 0
        for x in all_options:
            self.lc_advanced_options.InsertStringItem(counter, x[1])
            self.lc_advanced_options.SetStringItem(counter, 1, x[2])
            counter = counter + 1
        self.lc_advanced_options.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.lc_advanced_options.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        
# ---------------------------------------------------------           
    def SetLanguage(self, event):
        dlg = wx.Dialog(self, -1, '', size=(230, 300))
        l_dir = os.path.join(SYSLOC, 'locale')
        langs_arr = []
        for f in os.listdir(l_dir):
            if os.path.isdir(os.path.join(l_dir, f)):
                try:
                    yy= wx.Locale.FindLanguageInfo(f)
                    langs_arr.append(yy.Language)
                except Exception, expt:
                    pass
        langs = tuple(langs_arr)
        lang = wx.LANGUAGE_DEFAULT
        
        #controls
        self.langCtrl = langlistctrl.LanguageListCtrl(dlg, -1, filter=langlistctrl.LC_ONLY, only=langs)#, select=lang)
        but_ok = wx.Button(dlg, wx.ID_OK)
        but_cancel = wx.Button(dlg, wx.ID_CANCEL)
        
        #sizers
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.langCtrl, 1, wx.EXPAND|wx.ALL, 5)
        sizer2.Add(but_ok, 0, wx.EXPAND|wx.ALL, 5)
        sizer2.Add(but_cancel, 0, wx.EXPAND|wx.ALL, 5)
        sizer.Add(sizer2, 0, wx.EXPAND|wx.ALL, 5)
        dlg.SetSizer(sizer)
        
        if dlg.ShowModal() == wx.ID_OK:
            # get selected
            lang = self.langCtrl.GetLanguage()
            # save to database
            options.SetSetting('language-selected', str(lang), self.FILEDB)
            # update text
            ##self.parent.initI18n(lang)
        dlg.Destroy()
        
# --------------------------------------------------------- 
    def OnBrowseClick(self, event):
        dialog = wx.DirDialog(None, "Choose a directory:")
        if dialog.ShowModal() == wx.ID_OK:
            #print dialog.GetPath()
            self.tc_download_directory.SetValue(dialog.GetPath())
            #self.SaveOptions(None)
        dialog.Destroy()
        
# --------------------------------------------------------- 
    def OnClearCacheClick(self, event):
        #clear the cache
        temp_dir = system_files.GetDirectories(self).TempDirectory()
        file_cache.CheckCache(temp_dir, 0)
    
# --------------------------------------------------------- 
    def OnLastfmTestClick(self, event):
        #check last.fm        
        self.st_lastfm_status.SetLabel(self.parent.panel.SetScrobb())
                    
# ===================================================================
        
    def SetScrobbleMenuItem(self):
        self.parent.panel.SetScrobbleMenu()

            

    
