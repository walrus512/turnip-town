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
import sqlite3
import wx.xrc as xrc
from wx.lib import langlistctrl

from main_utils.read_write_xml import xml_utils
from main_utils import system_files
from main_utils import string_tools
from main_utils import options

import sys, os

OPTIONS_ARR = [ 'last_password',
                'last_user',
                'list_clear',
                #'alternate_source',
                'search_noid',
                'double_click',
                'win_pos',
                'gs_wait',
                'song_time',
                'scrobble_port',
                'scrobble_album',
                #'bitrate', 
                'record_dir',
                'tray',
                'autosave',
                'scrobble',
                'prefetch',
                'backend',
                'wxbackend'
                ]

OP_ARR = [
    ['m_cb_add-all-clear', 0],
    ['m_cb_search-double-click', 0],
    ['m_cb_search-results-drop-id', 0],
    ['m_cb_tray-minimize', 0],
    ['m_tc_download-directory', ''],
    ['m_cb_download-autosave', 0],
    #
    ['m_tc_lastfm-username', ''],
    ['m_tc_lastfm-password', ''],
    ['m_tc_proxy-url', ''],
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
        self.lb_options = xrc.XRCCTRL(self, 'm_lb_options')
        self.lc_advanced_options = xrc.XRCCTRL(self, 'm_lc_advanced_options')
        #self.tc_lastfm_username = xrc.XRCCTRL(self, 'm_tc_lastfm_username')
        #self.tc_lastfm_password = xrc.XRCCTRL(self, 'm_tc_lastfm_password')
        #self.st_option_name = xrc.XRCCTRL(self, 'm_st_option_name')
        self.tc_new_name = xrc.XRCCTRL(self, 'm_tc_new_name')
        self.tc_new_value = xrc.XRCCTRL(self, 'm_tc_new_value')
        
        self.lc_advanced_options.InsertColumn(0,"Option Name")
        self.lc_advanced_options.InsertColumn(1,"Option Value")
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.DisplayOption, self.lc_advanced_options)
        
        # bindings ----------------
        #self.Bind(wx.EVT_BUTTON, self.OnUpdateOption, id=xrc.XRCID('m_bu_update_option'))
        self.Bind(wx.EVT_BUTTON, self.OnAddOption, id=xrc.XRCID('m_bu_add_option'))
        self.Bind(wx.EVT_BUTTON, self.OnSaveClick, id=xrc.XRCID('m_bu_ok'))
        self.Bind(wx.EVT_BUTTON, self.OnExitClick, id=xrc.XRCID('m_bu_cancel'))
        self.Bind(wx.EVT_BUTTON, self.SetLanguage, id=xrc.XRCID('m_bu_options_language'))
        
            
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
                    xrc.XRCCTRL(self, x[0]).SetValue(int(setting_value))
        
    def SaveOptions(self):
        """ saves options to file """
        for x in OP_ARR:
            setting_value = str(xrc.XRCCTRL(self, x[0]).GetValue())            
            if setting_value != '':
                if setting_value == 'True':
                    setting_value = '1'
                if setting_value == 'False':
                    setting_value = '0'
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
        
    def OnUpdateOption(self, event):
        print 'frrf'
        
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
        
              
                
# ===================================================================
class Options(object):
    def __init__(self, parent):
        self.parent = parent
        self.save_location = system_files.GetDirectories(self.parent).DataDirectory()
       
    def LoadOptions(self):
        # load options from file, populate options tab
        options_dict = xml_utils().get_generic_settings(self.save_location + os.sep + 'settings.xml')
        if len(options_dict) > 1:
            password = options_dict['last_password']
            if password == None:
                password =''
            user = options_dict['last_user']
            if user == None:
                user =''
            self.parent.tc_options_password.SetValue(password)
            self.parent.tc_options_username.SetValue(user)
            
            #screen position
            xpos =  int(options_dict['win_pos'].split(',')[0][1:])
            if (xpos > (wx.GetDisplaySize()[0] - 50)) | (xpos < 0):
                xpos = 0
            ypos = int(options_dict['win_pos'].split(',')[1][:-1])
            if (ypos > (wx.GetDisplaySize()[1] - 50)) | (ypos < 0):
                ypos = 20
            self.parent.GetParent().SetPosition((xpos, ypos))            
            
            self.parent.cb_options_list_clear.SetValue(int(options_dict['list_clear']))            
            #self.parent.cb_options_alternate.SetValue(int(options_dict['alternate_source']))
            if options_dict.has_key('search_noid'):
                self.parent.cb_options_noid.SetValue(int(options_dict['search_noid']))
            #if options_dict.has_key('bitrate'):
            #    self.parent.ch_options_bitrate.SetStringSelection(options_dict['bitrate'])
            if options_dict.has_key('gs_wait'):
                self.parent.sc_options_gs_wait.SetValue(int(options_dict['gs_wait']))
            if options_dict.has_key('scrobble_port'):
                self.parent.rx_options_scrobble_port.SetSelection(int(options_dict['scrobble_port']))
            #if options_dict.has_key('backend'):
                #self.parent.rx_options_backend.SetSelection(int(options_dict['backend']))
            #if options_dict.has_key('wxbackend'):
                #self.parent.ch_options_wxbackend.SetSelection(int(options_dict['wxbackend']))
            if options_dict.has_key('scrobble_album'):
                self.parent.cb_options_scrobble_album.SetValue(int(options_dict['scrobble_album']))
            if options_dict.has_key('tray'):
                self.parent.cb_options_tray.SetValue(int(options_dict['tray']))
            if options_dict.has_key('autosave'):
                self.parent.cb_options_autosave.SetValue(int(options_dict['autosave']))
            if options_dict.has_key('scrobble'):
                self.parent.cb_options_scrobble.SetValue(int(options_dict['scrobble']))
            if options_dict.has_key('prefetch'):
                self.parent.cb_options_prefetch.SetValue(int(options_dict['prefetch']))                
            if options_dict.has_key('cache_size'):
                self.parent.sl_options_cache_size.SetValue(int(options_dict['cache_size']))                
            if options_dict.has_key('record_dir'):
                if options_dict['record_dir'] != None:                    
                    self.parent.bu_options_record_dir.SetLabel(options_dict['record_dir'])
            else:
                self.parent.bu_options_record_dir.SetLabel(self.save_location + '\\mp3s\\')
            if options_dict.has_key('song_time'):
                fmt_time = ConvertTimeFormated(int(options_dict['song_time']))
                minutes = fmt_time.split(':')[0]
                seconds = fmt_time.split(':')[1]
                self.parent.sc_options_song_minutes.SetValue(int(minutes))
                self.parent.sc_options_song_seconds.SetValue(int(seconds))
            self.parent.rx_options_double_click.SetSelection(int(options_dict['double_click']))
        
        #set the scrobble menu item checkmark
        self.SetScrobbleMenuItem()
            
    def SaveOptions(self):
        # save value to options.xml
        #print (self.search_settings_tree)
        
        window_dict = {}        
        # **
        try:        
            window_dict['last_password'] = string_tools.unescape(self.parent.tc_options_password.GetValue())
            window_dict['last_user'] = string_tools.unescape(self.parent.tc_options_username.GetValue())
        except Exception, expt:
            print "SaveOptions: " + str(Exception) + str(expt)
        #str(int( to convert true/fales to 1/0
        window_dict['list_clear'] = str(int(self.parent.cb_options_list_clear.GetValue()))
        #window_dict['alternate_source'] = str(int(self.parent.cb_options_alternate.GetValue()))
        window_dict['search_noid'] = str(int(self.parent.cb_options_noid.GetValue()))
        window_dict['double_click'] = str(int(self.parent.rx_options_double_click.GetSelection()))
        #window_dict['backend'] = str(int(self.parent.rx_options_backend.GetSelection()))
        #window_dict['wxbackend'] = str(int(self.parent.ch_options_wxbackend.GetSelection()))
        window_dict['win_pos'] = str(self.parent.GetParent().GetPosition())
        window_dict['gs_wait'] = str(self.parent.sc_options_gs_wait.GetValue())
        window_dict['scrobble_port'] = str(int(self.parent.rx_options_scrobble_port.GetSelection()))
        window_dict['scrobble_album'] = str(int(self.parent.cb_options_scrobble_album.GetValue()))
        window_dict['tray'] = str(int(self.parent.cb_options_tray.GetValue()))
        window_dict['autosave'] = str(int(self.parent.cb_options_autosave.GetValue()))
        window_dict['scrobble'] = str(int(self.parent.cb_options_scrobble.GetValue()))
        window_dict['prefetch'] = str(int(self.parent.cb_options_prefetch.GetValue()))
        #window_dict['bitrate'] = str(self.parent.ch_options_bitrate.GetStringSelection())
        #**
        try:
            window_dict['record_dir'] = string_tools.unescape(self.parent.bu_options_record_dir.GetLabel())
        except Exception, expt:
            print "SaveOptions: " + str(Exception) + str(expt)
        window_dict['cache_size'] = str(self.parent.sl_options_cache_size.GetValue())
        
        minutes = self.parent.sc_options_song_minutes.GetValue()
        seconds = self.parent.sc_options_song_seconds.GetValue()
        formated_time = str(minutes) + ':' + str(seconds)
        converted = str(ConvertTimeSeconds(formated_time))
        window_dict['song_time'] = str(converted)
        
        #set the scrobble menu item checkmark
        self.SetScrobbleMenuItem()
        
        #if (window_dict['alternate_source'] == '1'):
        #    dlg = wx.MessageDialog(self.parent, 'Warning!\r\nUsing the alternate GrooveShark source may cause HUGE problems when using the GrooveShark website (ie. it will not work for you anymore).\r\nSave anyway?', 'Alert', wx.CANCEL | wx.OK | wx.ICON_WARNING)
        #    if (dlg.ShowModal() == wx.ID_OK):
        #        #save new settings        
        #        xml_utils().save_generic_settings(self.save_location + os.sep + 'settings.xml', 'settings.xml', window_dict)
        #        #print window_dict
        #    else:
        #        self.parent.cb_options_alternate.SetValue(0)
        #    dlg.Destroy()
            
        #else:
        #save new settings        
        xml_utils().save_generic_settings(self.save_location  + os.sep, 'settings.xml', window_dict)
        #print window_dict 
        
    def SetScrobbleMenuItem(self):
        if self.parent.cb_options_scrobble.IsChecked():
            self.parent.lastfm_toggle.Check(True)
        else:
            self.parent.lastfm_toggle.Check(False)
            
#-------------------------------------------------
#-------------------------------------------------
        
def ConvertTimeFormated(seconds):
    # convert seconds to mm:ss
    return str(float(seconds) / float(60)).split('.')[0] + ':' + str(abs(seconds) % 60).zfill(2)
        
def ConvertTimeSeconds(formated_time):
    # convert mm:ss to seconds
    return (int(formated_time.split(':')[0]) * 60) + (int(formated_time.split(':')[1]))
    
