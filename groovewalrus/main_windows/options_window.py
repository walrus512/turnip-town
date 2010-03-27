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

from main_utils.read_write_xml import xml_utils
from main_utils import system_files

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
                'prefetch'
                ]

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
        
        window_dict['last_password'] = self.parent.tc_options_password.GetValue()
        window_dict['last_user'] = self.parent.tc_options_username.GetValue()
        #str(int( to convert true/fales to 1/0
        window_dict['list_clear'] = str(int(self.parent.cb_options_list_clear.GetValue()))
        #window_dict['alternate_source'] = str(int(self.parent.cb_options_alternate.GetValue()))
        window_dict['search_noid'] = str(int(self.parent.cb_options_noid.GetValue()))
        window_dict['double_click'] = str(int(self.parent.rx_options_double_click.GetSelection()))
        window_dict['win_pos'] = str(self.parent.GetParent().GetPosition())
        window_dict['gs_wait'] = str(self.parent.sc_options_gs_wait.GetValue())
        window_dict['scrobble_port'] = str(int(self.parent.rx_options_scrobble_port.GetSelection()))
        window_dict['scrobble_album'] = str(int(self.parent.cb_options_scrobble_album.GetValue()))
        window_dict['tray'] = str(int(self.parent.cb_options_tray.GetValue()))
        window_dict['autosave'] = str(int(self.parent.cb_options_autosave.GetValue()))
        window_dict['scrobble'] = str(int(self.parent.cb_options_scrobble.GetValue()))
        window_dict['prefetch'] = str(int(self.parent.cb_options_prefetch.GetValue()))
        #window_dict['bitrate'] = str(self.parent.ch_options_bitrate.GetStringSelection())
        window_dict['record_dir'] = str(self.parent.bu_options_record_dir.GetLabel())
        
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
            
    def ShowAbout(self, program_name, program_version):
        # First we create and fill the info object
        info = wx.AboutDialogInfo()
        info.Name = program_name
        info.Version = program_version
        info.Copyright = "(c) 1906 - 2018"
        info.Description = """
Products Used
==========
Groove Shark - http://grooveshark.com
Last.fm - http://last.fm
Music Brainz - http://musicbrainz.org
---
Python - http://www.python.org
wxpython - http://www.wxpython.org
wxFormBuilder - http://wxformbuilder.org
py2exe - http://www.py2exe.org
---
pyMedia - http://pymedia.org
Kaa Metadata - http://doc.freevo.org/2.0/Kaa
EventGhost - http://sourceforge.net/projects/eventghost/
GrooveShark.py - Zimmmer: http://hak5.org
GrooveShark PyApi - http://github.com/Tim-Smart/grooveshack
PyLast.py - http://code.google.com/p/pylast/
---
Tango Icons - http://tango.freedesktop.org
"Walrus" Photo - http://picasaweb.google.com/dschmitz
"Gw" Icon - http://tinylab.deviantart.com/
"""
        info.WebSite = ("http://groove-walrus.turnip-town.net", "http://groove-walrus.turnip-town.net")

        # Then we call wx.AboutBox giving it that info object
        wx.AboutBox(info)
        
        
def ConvertTimeFormated(seconds):
    # convert seconds to mm:ss
    return str(float(seconds) / float(60)).split('.')[0] + ':' + str(abs(seconds) % 60).zfill(2)
        
def ConvertTimeSeconds(formated_time):
    # convert mm:ss to seconds
    return (int(formated_time.split(':')[0]) * 60) + (int(formated_time.split(':')[1]))
    
def GetSetting(setting_name):
    #get a value from the settings table
    conn = sqlite3.connect(FILEDB)
    c = conn.cursor()
    tq = "SELECT setting_value FROM m_settings WHERE setting_name = '%s'" % setting_name
    c.execute(tq)
    h = c.fetchall()
    print h
    return (h)

def SetSetting(setting_name, setting_value):
    #set a value from the settings table        
    conn = sqlite3.connect(FILEDB)
    c = conn.cursor()    
    t = 'SELECT setting_id FROM m_settings WHERE setting_name= "%s"' % setting_name
    c.execute(t)
    h = c.fetchall()
    print h
    if len(h) >= 1:
        g_setting_id = h[0][0]        
        c.execute('UPDATE m_settings SET setting_value="%s" WHERE setting_id =%i' % (setting_value, g_setting_id))
        conn.commit()
    else:
        c.execute('INSERT INTO m_settings values (null,?,?)', (setting_name, setting_value))
        conn.commit()
    c.close()
