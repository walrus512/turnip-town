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
from wx.lib.pubsub import Publisher as pub
import os #, sys
#import re

from main_utils.read_write_xml import xml_utils
from main_utils import system_files

#http://webservices.lyrdb.com/lookup.php?q=the%20shins|new%20slang&for=match&agent=agent
#s00575423\New Slang\THE SHINS 
#a00052177\New Slang\THE SHINS 
#t00092063\New Slang\The Shins
#t00113827\New Slang\The Shins
#http://www.lyrdb.com/getlyr.php?q=id


#SYSLOC = os.getcwd()
#LYRICS_SETTINGS = os.path.join(os.getcwd(), 'plugins','lyrics') + os.sep + "settings_lyrics.xml"
LYRICS = os.path.join(os.getcwd(), 'plugins','lyrics') + os.sep
RESFILE = os.path.join(os.getcwd(), 'plugins','lyrics') + os.sep + "layout_lyrics.xml"


class MainPanel(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, "Lyrics", size=(375,460), style=wx.FRAME_SHAPED|wx.RESIZE_BORDER) #STAY_ON_TOP)        
        self.parent = parent
        x = MyPanel(self, parent)
        
class MyPanel(wx.Panel):
    def __init__(self, dialog, parent):
        wx.Panel.__init__(self, dialog, -1)
        self.parent = parent
        self.dialog = dialog
        
        self.LYRICS_SETTINGS = system_files.GetDirectories(self).MakeDataDirectory('plugins') + os.sep

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
        self.bm_lyrics_tab = xrc.XRCCTRL(self, 'm_bm_lyrics_tab')
        self.bm_lyrics_tab.Show(False)
        #self.st_lyrics_song = xrc.XRCCTRL(self, 'm_st_lyrics_song')
        self.rb_lyrics_lazy = xrc.XRCCTRL(self, 'm_rb_lyrics_lazy')
        self.ch_lyrics_song_list = xrc.XRCCTRL(self, 'm_ch_lyrics_song_list')
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
        self.bm_lyrics_tab.Bind(wx.EVT_LEFT_UP, self.OnMakeTabClick)
        
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self.st_lyrics_header.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.st_lyrics_header.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.st_lyrics_header.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.st_lyrics_header.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)       
        self.Bind(wx.EVT_CHOICE, self.EvtChoice, self.ch_lyrics_song_list)
        self.Bind(wx.EVT_RADIOBUTTON, self.EvtRadio, self.rb_lyrics_lazy)
        self.Bind(wx.EVT_RADIOBUTTON, self.EvtRadio, id=xrc.XRCID('m_rb_lyrics_strict'))
        
        #self.bu_update_restart.Enable(False)    
        # set layout --------------
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel, 1, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.LoadSettings()
        #self.CopyReplace()
        #self.OnChars()
        #xrc.XRCCTRL(self, 'm_notebook1').SetPageText(1, '@' + self.tc_lyrics_username.GetValue())
        
        self.current_song = ''
        
        self.GetLyrics(None)
        self.parent.SetReceiver(self)        
        
        # hotkeys ------------------
        ctrlrID = 802
        ctrleqID = 902
        ctrlmiID = 901
        
        self.aTable_values = [
               (wx.ACCEL_CTRL, ord('R'), ctrlrID),
               (wx.ACCEL_CTRL, ord('='), ctrleqID),
               (wx.ACCEL_CTRL, ord('-'), ctrlmiID)
                                ]
        aTable = wx.AcceleratorTable(self.aTable_values)
        #add to main program
        self.SetAcceleratorTable(aTable) 
        wx.EVT_MENU(self, ctrlrID, self.ResetPosition)
        wx.EVT_MENU(self, ctrleqID, self.IncreaseFontSize)
        wx.EVT_MENU(self, ctrlmiID, self.DecreaseFontSize)

    def PlaybackReceiverAction(self, message):
        #pubsub receiver actions
        #print message.data
        self.GetLyrics(None)
        
    def ResetPosition(self, event):
        #resets the winodws position
        self.dialog.SetSize((375,460))
        self.dialog.SetPosition((50,50))
        
    def IncreaseFontSize(self, event):
        font_size = self.tc_lyrics_text.GetFont().GetPointSize()        
        self.tc_lyrics_text.SetFont( wx.Font(font_size + 1, wx.NORMAL, wx.NORMAL, wx.NORMAL) )
        self.Refresh()
        
    def DecreaseFontSize(self, event):
        font_size = self.tc_lyrics_text.GetFont().GetPointSize()
        if font_size >= 4:
            self.tc_lyrics_text.SetFont( wx.Font(font_size - 1, wx.NORMAL, wx.NORMAL, wx.NORMAL) )
        self.Refresh()
        
    def EvtChoice(self, event):
        self.current_song = ''
        
    def EvtRadio(self, event):
        self.current_song = ''
        
    def GetLyrics(self, event):
        #get some lyrics for the playing song
        #http://webservices.lyrdb.com/lookup.php?q=the%20shins|new%20slang&for=match&agent=agent
        use_selection = 0
        if self.ch_lyrics_song_list.GetSelection() >= 0:
            use_selection = self.ch_lyrics_song_list.GetSelection()
           
        if self.parent.partist !='':
            query_string_value = self.parent.partist + ' - ' + self.parent.ptrack
            if self.current_song != query_string_value:
                self.current_song = query_string_value
                if self.rb_lyrics_lazy.GetValue() == True:
                    query_string = 'http://webservices.lyrdb.com/lookup.php?q=' + query_string_value + '&for=fullt&agent=GrooveWalrus/0.2'
                else:
                    query_string_value = self.parent.partist + '|' + self.parent.ptrack
                    query_string = 'http://webservices.lyrdb.com/lookup.php?q=' + query_string_value + '&for=match&agent=GrooveWalrus/0.2'
                query_string = url_quote(query_string)
                #print query_string
                url_connection = urllib.urlopen(query_string.replace(' ', '+'))
                raw_results = url_connection.read()                
                
                results_array = raw_results.split('\n')        
                #print results_array
                self.ch_lyrics_song_list.Clear()
                for x in results_array:
                    y = x.split('\\')[1]
                    self.ch_lyrics_song_list.Append(y)
                if len(results_array) >= 1:
                    if use_selection > (len(results_array) - 1):
                        use_selection = 0
                    self.ch_lyrics_song_list.SetSelection(use_selection)                    
                lyrics_id = results_array[use_selection].split('\\')[0]
                                
                #print lyrics_id
                
                #http://www.lyrdb.com/getlyr.php?q=id
                lyrics_query = 'http://www.lyrdb.com/getlyr.php?q=' + lyrics_id
                lyrics_query = url_quote(lyrics_query)
                url_connection = urllib.urlopen(lyrics_query.replace(' ', '+'))
                raw_results = url_connection.read()
                #print raw_results                
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
                self.tc_lyrics_text.SetValue(raw_results) # + '\r\n http://www.lyrdb.com')
            
        
    def ErrorMessage(self):
            dlg = wx.MessageDialog(self, "Username/password not entered", 'Alert', wx.OK | wx.ICON_WARNING)
            if (dlg.ShowModal() == wx.ID_OK):
                dlg.Destroy()
            
    def CloseMe(self, event=None):
        self.SaveOptions()
        self.parent.KillReceiver(self.PlaybackReceiverAction)
        self.dialog.Destroy()
        
    def LoadSettings(self):
        #load the setting from settings_lyrics.xml if it exists
        settings_dict = xml_utils().get_generic_settings(self.LYRICS_SETTINGS + "settings_lyrics.xml")
        #print settings_dict
        if len(settings_dict) >= 1:
            if settings_dict.has_key('window_position'):
                # not good, replace eval
                self.dialog.SetPosition(eval(settings_dict['window_position']))
            if settings_dict.has_key('window_size'):
                self.dialog.SetSize(eval(settings_dict['window_size']))

    def SaveOptions(self, event=None):
        # save value to options.xml
        window_dict = {}
        window_dict['window_position'] = str(self.dialog.GetScreenPosition())
        window_dict['window_size'] = str(self.dialog.GetSize())#[0], self.GetSize()[1]))
        
        xml_utils().save_generic_settings(self.LYRICS_SETTINGS, "settings_lyrics.xml", window_dict)

    def OnMakeTabClick(self, event=None):
        # transfer plug-in to tab in main player
        # make a new page                
        page1 = PageOne(self.parent.nb_main, self.parent)
        # add the pages to the notebook
        self.parent.nb_main.AddPage(page1, "Lyrics")
     
        self.Destroy()        
            
# --------------------------------------------------------- 
# titlebar-like move and drag
    
    def OnMouseLeftDown(self, evt):
        self.Refresh()
        self.ldPos = evt.GetEventObject().ClientToScreen(evt.GetPosition())
        self.wPos = self.dialog.ClientToScreen((0,0))
        self.CaptureMouse()

    def OnMouseMotion(self, evt):
        if evt.Dragging() and evt.LeftIsDown():
            try:            
                dPos = evt.GetEventObject().ClientToScreen(evt.GetPosition())
                #nPos = (self.wPos.x + (dPos.x - self.ldPos.x), -2)
                nPos = (self.wPos.x + (dPos.x - self.ldPos.x), self.wPos.y + (dPos.y - self.ldPos.y))
                self.dialog.Move(nPos)
            except AttributeError:
                pass

    def OnMouseLeftUp(self, evt):
        try:
            self.ReleaseMouse()
        except wx._core.PyAssertionError:
            pass

    def OnRightUp(self, evt):
        #self.hide_me()
        #self..Destroy()
        pass
        
# --------------------------------------------------------- 
            
class PageOne(wx.Panel):
    def __init__(self, parent, grandparent):
        wx.Panel.__init__(self, parent)
        self.parent = grandparent
        
            
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
    #s = urllib.quote(s)#, safe)
    if want_unicode:
        s = s.decode(charset) # ascii would also work
    return s
     
# ===================================================================   
