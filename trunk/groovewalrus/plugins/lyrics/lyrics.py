"""
GrooveWalrus: Lyrics Plug-in 
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

import urllib
#import urllib2

import wx
import wx.xrc as xrc
import os #, sys
#import re

#from main_utils.read_write_xml import xml_utils
#from main_utils import system_files

#http://webservices.lyrdb.com/lookup.php?q=the%20shins|new%20slang&for=match&agent=agent
#s00575423\New Slang\THE SHINS 
#a00052177\New Slang\THE SHINS 
#t00092063\New Slang\The Shins
#t00113827\New Slang\The Shins
#http://www.lyrdb.com/getlyr.php?q=id


#SYSLOC = os.getcwd()
#TWITTER_SETTINGS = os.path.join(os.getcwd(), 'plugins','lyrics') + os.sep + "settings_lyrics.xml"
LYRICS = os.path.join(os.getcwd(), 'plugins','lyrics') + os.sep
RESFILE = os.path.join(os.getcwd(), 'plugins','lyrics') + os.sep + "layout_lyrics.xml"


class MainPanel(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, "Lyrics", size=(375,460), style=wx.FRAME_SHAPED) #STAY_ON_TOP)        
        self.parent = parent
        
        #self.TWITTER_SETTINGS = system_files.GetDirectories(self).MakeDataDirectory('plugins') + os.sep
        
        
        # XML Resources can be loaded from a file like this:
        res = xrc.XmlResource(RESFILE)

        # Now create a panel from the resource data
        panel = res.LoadPanel(self, "m_pa_plugin_lyrics")

        # control references --------------------
        self.tc_lyrics_text = xrc.XRCCTRL(self, 'm_tc_lyrics_text')
        #self.tc_lyrics_username = xrc.XRCCTRL(self, 'm_tc_lyrics_username')
        #self.tc_lyrics_password = xrc.XRCCTRL(self, 'm_tc_lyrics_password')
        #self.tc_lyrics_default = xrc.XRCCTRL(self, 'm_tc_lyrics_default')
        #self.st_lyrics_chars = xrc.XRCCTRL(self, 'm_st_lyrics_chars')
        #header for dragging and moving
        self.st_lyrics_header = xrc.XRCCTRL(self, 'm_st_lyrics_header')
        self.bm_lyrics_close = xrc.XRCCTRL(self, 'm_bm_lyrics_close')
        self.st_lyrics_song = xrc.XRCCTRL(self, 'm_st_lyrics_song')
        #self.hw_lyrics_at = xrc.XRCCTRL(self, 'm_hw_lyrics_at')

        # bindings ----------------
        #self.Bind(wx.EVT_BUTTON, self.SaveOptions, id=xrc.XRCID('m_bu_lyrics_save'))
        #self.Bind(wx.EVT_BUTTON, self.Twat, id=xrc.XRCID('m_bu_lyrics_tweet'))
        
        self.Bind(wx.EVT_BUTTON, self.GetLyrics, id=xrc.XRCID('m_bu_lyrics_update'))
        #self.Bind(wx.EVT_BUTTON, self.GetMentions, id=xrc.XRCID('m_bu_lyrics_update_at'))
        #self.Bind(wx.EVT_BUTTON, self.CopyReplace, id=xrc.XRCID('m_bu_lyrics_update_default'))
        
        #self.hw_lyrics_home.Bind(wx.html.EVT_HTML_LINK_CLICKED, self.OnWebClick)
        #self.hw_lyrics_at.Bind(wx.html.EVT_HTML_LINK_CLICKED, self.OnWebClick)
        
        #self.Bind(wx.EVT_TEXT, self.OnChars, self.tc_lyrics_text)
        self.bm_lyrics_close.Bind(wx.EVT_LEFT_UP, self.CloseMe)
        
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self.st_lyrics_header.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.st_lyrics_header.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.st_lyrics_header.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.st_lyrics_header.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)       

            
        #self.bu_update_restart.Enable(False)    
        # set layout --------------
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel, 1, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        #self.LoadSettings()
        #self.CopyReplace()
        #self.OnChars()
        #xrc.XRCCTRL(self, 'm_notebook1').SetPageText(1, '@' + self.tc_lyrics_username.GetValue())
            
        
    def GetLyrics(self, event):
        #get some lyrics for the playing song
        #http://webservices.lyrdb.com/lookup.php?q=the%20shins|new%20slang&for=match&agent=agent
        if self.parent.partist !='':
            query_string_value = self.parent.partist + '-' + self.parent.ptrack
            self.st_lyrics_song.SetLabel(self.parent.partist + ' - ' + self.parent.ptrack)
            query_string = 'http://webservices.lyrdb.com/lookup.php?q=' + query_string_value + '&for=fullt&agent=GrooveWalrus/0.2'
        
            query_string = url_quote(query_string)
            url_connection = urllib.urlopen(query_string.replace(' ', '+'))
            raw_results = url_connection.read()
        
            results_array = raw_results.split('\n')        
            #print results_array
            lyrics_id = results_array[0].split('\\')[0]
            #print lyrics_id
            
            #http://www.lyrdb.com/getlyr.php?q=id
            lyrics_query = 'http://www.lyrdb.com/getlyr.php?q=' + lyrics_id
            lyrics_query = url_quote(lyrics_query)
            url_connection = urllib.urlopen(lyrics_query.replace(' ', '+'))
            raw_results = url_connection.read()        
            #print raw_results
            #raw_results = raw_results.replace('\n\n', '\n')
            #raw_results = raw_results.replace('\r\n\r\n', '\r\n')
            #get rid of double spacing
            #print raw_results.split('\n\n\n\n')
            if len(raw_results.split('\n\n\n\n')) > 1:
                raw_results = raw_results.replace('\n\n', '\n')
            if len(raw_results.split('\r\r\n\r\r\n')) > 1:
                raw_results = raw_results.replace('\r\r\n', '\r\n')
            if len(raw_results.split('\r\n\r\n\r\n\r\n')) > 1:
                raw_results = raw_results.replace('\r\n\r\n', '\r\n')              
            self.tc_lyrics_text.SetValue(raw_results + '\r\n http://www.lyrdb.com')
        
        
    def ErrorMessage(self):
            dlg = wx.MessageDialog(self, "Username/password not entered", 'Alert', wx.OK | wx.ICON_WARNING)
            if (dlg.ShowModal() == wx.ID_OK):
                dlg.Destroy()
            
    def CloseMe(self, event=None):
        self.Destroy()
        
    def LoadSettings(self):
        #load the setting from settings_lyrics.xml if it exists
        settings_dict = xml_utils().get_generic_settings(self.TWITTER_SETTINGS + "settings_lyrics.xml")
        #print settings_dict
        if len(settings_dict) >= 1:
            username=''
            if settings_dict.has_key('username'):
                username = settings_dict['username']
            password =''
            if settings_dict.has_key('password'):
                password = settings_dict['password']
            default_text=''
            if settings_dict.has_key('default_text'):
                default_text = settings_dict['default_text']

            self.tc_lyrics_username.SetValue(username)
            self.tc_lyrics_password.SetValue(password)   
            self.tc_lyrics_default.SetValue(default_text)

    def SaveOptions(self, event):
        # save value to options.xml
        window_dict = {}        
        window_dict['password'] = self.tc_lyrics_password.GetValue()
        window_dict['username'] = self.tc_lyrics_username.GetValue()
        window_dict['default_text'] = self.tc_lyrics_default.GetValue()
        
        xml_utils().save_generic_settings(self.TWITTER_SETTINGS, "settings_lyrics.xml", window_dict)

            
# --------------------------------------------------------- 
# titlebar-like move and drag
    
    def OnMouseLeftDown(self, evt):
        self.Refresh()
        self.ldPos = evt.GetEventObject().ClientToScreen(evt.GetPosition())
        self.wPos = self.ClientToScreen((0,0))
        self.CaptureMouse()

    def OnMouseMotion(self, evt):
        if evt.Dragging() and evt.LeftIsDown():
            dPos = evt.GetEventObject().ClientToScreen(evt.GetPosition())
            #nPos = (self.wPos.x + (dPos.x - self.ldPos.x), -2)
            nPos = (self.wPos.x + (dPos.x - self.ldPos.x), self.wPos.y + (dPos.y - self.ldPos.y))
            self.Move(nPos)

    def OnMouseLeftUp(self, evt):
        try:
            self.ReleaseMouse()
        except wx._core.PyAssertionError:
            pass

    def OnRightUp(self, evt):
        self.hide_me()
        #self..Destroy()
        
# --------------------------------------------------------- 
            
           
# ===================================================================            

              
charset = 'utf-8'
        
def url_quote(s, safe='/', want_unicode=False):
    """
    Wrapper around urllib.quote doing the encoding/decoding as usually wanted:
    
    @param s: the string to quote (can be str or unicode, if it is unicode,
              config.charset is used to encode it before calling urllib)
    @param safe: just passed through to urllib
    @param want_unicode: for the less usual case that you want to get back
                         unicode and not str, set this to True
                         Default is False.
    """
    if isinstance(s, unicode):
        s = s.encode(charset)
    elif not isinstance(s, str):
        s = str(s)
    #s = urllib.quote(s, safe)
    if want_unicode:
        s = s.decode(charset) # ascii would also work
    return s
     
# ===================================================================   
