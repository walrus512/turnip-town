"""
GrooveWalrus: Twitter Plug-in 
Copyright (C) 2009, 2010
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
import urllib2

import wx
import wx.xrc as xrc
##from wx.lib.pubsub import Publisher as pub
import sys, os
import re

from main_utils.read_write_xml import xml_utils
from main_utils import system_files
from main_utils import default_app_open

import api

#SYSLOC = os.getcwd()
TWITTER_UPDATE = 'http://twitter.com/statuses/update.xml'
#TWITTER_SETTINGS = os.path.join(os.getcwd(), 'plugins','twitter') + os.sep + "settings_twitter.xml"
TWITTER = os.path.join(os.getcwd(), 'plugins','twitter') + os.sep
RESFILE = os.path.join(os.getcwd(), 'plugins','twitter') + os.sep + "layout_twitter.xml"


class MainPanel(wx.Dialog):
    def __init__(self, parent, pathToPlugins=None):
        if(not pathToPlugins==None):
            RESFILE = os.path.join(pathToPlugins,'twitter') + os.sep + "layout_twitter.xml"
            TWITTER = os.path.join(pathToPlugins,'twitter') + os.sep
        
        wx.Dialog.__init__(self, parent, -1, "Twitter", size=(475,510), style=wx.FRAME_SHAPED|wx.RESIZE_BORDER) #STAY_ON_TOP)        
        self.parent = parent
        
        self.TWITTER_SETTINGS = system_files.GetDirectories(self).MakeDataDirectory('plugins') + os.sep
        
        
        # XML Resources can be loaded from a file like this:
        res = xrc.XmlResource(RESFILE)

        # Now create a panel from the resource data
        panel = res.LoadPanel(self, "m_pa_plugin_twitter")

        # control references --------------------
        self.tc_twitter_text = xrc.XRCCTRL(self, 'm_tc_twitter_text')
        self.tc_twitter_username = xrc.XRCCTRL(self, 'm_tc_twitter_username')
        self.tc_twitter_password = xrc.XRCCTRL(self, 'm_tc_twitter_password')
        self.tc_twitter_default = xrc.XRCCTRL(self, 'm_tc_twitter_default')
        self.st_twitter_chars = xrc.XRCCTRL(self, 'm_st_twitter_chars')
        #header for dragging and moving
        self.st_twitter_header = xrc.XRCCTRL(self, 'm_st_twitter_header')
        self.bm_twitter_close = xrc.XRCCTRL(self, 'm_bm_twitter_close')
        self.hw_twitter_home = xrc.XRCCTRL(self, 'm_hw_twitter_home')
        self.hw_twitter_at = xrc.XRCCTRL(self, 'm_hw_twitter_at')

        # bindings ----------------
        self.Bind(wx.EVT_BUTTON, self.SaveOptions, id=xrc.XRCID('m_bu_twitter_save'))
        self.Bind(wx.EVT_BUTTON, self.Twat, id=xrc.XRCID('m_bu_twitter_tweet'))
        
        self.Bind(wx.EVT_BUTTON, self.GetHomeTimeline, id=xrc.XRCID('m_bb_twitter_update_home'))
        self.Bind(wx.EVT_BUTTON, self.GetMentions, id=xrc.XRCID('m_bb_twitter_update_at'))
        self.Bind(wx.EVT_BUTTON, self.CopyReplace, id=xrc.XRCID('m_bb_twitter_update_default'))
        
        self.hw_twitter_home.Bind(wx.html.EVT_HTML_LINK_CLICKED, self.OnWebClick)
        self.hw_twitter_at.Bind(wx.html.EVT_HTML_LINK_CLICKED, self.OnWebClick)
        
        self.Bind(wx.EVT_TEXT, self.OnChars, self.tc_twitter_text)
        self.bm_twitter_close.Bind(wx.EVT_LEFT_UP, self.CloseMe)
        
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self.st_twitter_header.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.st_twitter_header.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.st_twitter_header.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.st_twitter_header.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)       

            
        #self.bu_update_restart.Enable(False)    
        # set layout --------------
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel, 1, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.LoadSettings()
        self.CopyReplace()
        self.OnChars()
        xrc.XRCCTRL(self, 'm_notebook1').SetPageText(1, '@' + self.tc_twitter_username.GetValue())
        
        #pubsub receiver
        ##listener = self.parent.SetReceiver(self)

    ##def PlaybackReceiverAction(self, message):
        #pubsub receiver actions
        ##print message.data
        
    def GetHomeTimeline(self, event=None):
        username = self.tc_twitter_username.GetValue()
        password = self.tc_twitter_password.GetValue()
        if (username !='') & (password !=''):
            twitter = api.Twitter(username, password)
            # Get the public timeline
            x = twitter.statuses.home_timeline()
            html = ''
            for y in x:
                #<B><FONT COLOR="#FFFFFF"><FONT SIZE=+1>N</FONT></FONT></B>
                html = html + '<p><b><a href="' + y['user']['screen_name'] + '"><FONT COLOR="#336600">' + y['user']['screen_name'] + '</FONT></a></b> '
                ttext = self.LinkReplace(y['text'])
                html = html + '' + ttext + '</FONT><br>'            
                html = html + '<FONT SIZE=-2>' + y['created_at'] + '</FONT></p>'
                
            self.hw_twitter_home.SetPage(html)
        else:
            self.ErrorMessage()
            
    def GetMentions(self, event=None):
        username = self.tc_twitter_username.GetValue()
        password = self.tc_twitter_password.GetValue()
        if (username !='') & (password !=''):
            twitter = api.Twitter(username, password)
            # Get the public timeline
            x = twitter.statuses.mentions()
            html = ''
            for y in x:
                html = html + '<p><b><a href="' + y['user']['screen_name'] + '"><FONT COLOR="#336600">' + y['user']['screen_name'] + '</FONT></a></b> '
                ttext = self.LinkReplace(y['text'])
                html = html + '' + ttext + '</FONT><br>'            
                html = html + '<FONT SIZE=-2>' + y['created_at'] + '</FONT></p>'
                
            self.hw_twitter_at.SetPage(html)
        else:
            self.ErrorMessage()
            
    def LinkReplace(self, ttext):
        r1 = r"(\b(http|https)://([-A-Za-z0-9+&@#/%?=~_()|!:,.;]*[-A-Za-z0-9+&@#/%=~_()|]))"
        ttext = re.sub(r1,r'<a href="\1">\1</a>',ttext)
        return ttext
            
    def OnWebClick(self, event):
        mouse_type_id = event.GetLinkInfo().GetEvent().GetEventType()
        
        #check if it's a web link
        if event.GetLinkInfo().GetHref()[:4] == 'http':        
            default_app_open.dopen(event.GetLinkInfo().GetHref())
        else:
            if wx.EVT_LEFT_UP.typeId == mouse_type_id:
                self.Reply(event.GetLinkInfo().GetHref())
            else:
                #right click prepends existing data to reply
                self.Reply(event.GetLinkInfo().GetHref(), True)
            
    def ErrorMessage(self):
            dlg = wx.MessageDialog(self, "Username/password not entered", 'Alert', wx.OK | wx.ICON_WARNING)
            if (dlg.ShowModal() == wx.ID_OK):
                dlg.Destroy()
            
    def CloseMe(self, event=None):
        self.Destroy()
        
    def LoadSettings(self):
        #load the setting from settings_twitter.xml if it exists
        settings_dict = xml_utils().get_generic_settings(self.TWITTER_SETTINGS + "settings_twitter.xml")
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

            self.tc_twitter_username.SetValue(username)
            self.tc_twitter_password.SetValue(password)   
            self.tc_twitter_default.SetValue(default_text)

    def SaveOptions(self, event):
        # save value to options.xml
        window_dict = {}        
        window_dict['password'] = self.tc_twitter_password.GetValue()
        window_dict['username'] = self.tc_twitter_username.GetValue()
        window_dict['default_text'] = self.tc_twitter_default.GetValue()
        
        xml_utils().save_generic_settings(self.TWITTER_SETTINGS, "settings_twitter.xml", window_dict)

            
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
    def CopyReplace(self, event=None):     
        tt = self.tc_twitter_default.GetValue()
        tt = tt.replace('[artist]', self.parent.current_song.artist)
        tt = tt.replace('[song]', self.parent.current_song.song)
        self.tc_twitter_text.SetValue(tt)
        
    def Reply(self, reply_to, prepend=False):
        if prepend == True:
            #prepend the reply name
            self.tc_twitter_text.SetValue('@'+reply_to+' ' + self.tc_twitter_text.GetValue())
        else:
            #clear the field first
            self.tc_twitter_text.SetValue('@'+reply_to+' ')
        
    def OnChars(self, event=None):
        #print 'chars'
        self.st_twitter_chars.SetLabel(str(len(self.tc_twitter_text.GetValue())) + "/140 characters")
        
# ---------------------------------------------------------    
    def Twat(self, event):
    
        #replace
        twit_text = self.tc_twitter_text.GetValue()
        password = self.tc_twitter_password.GetValue()
        username = self.tc_twitter_username.GetValue()
        twit_text = url_quote(twit_text)
    
        if (len(twit_text) > 0) and (len(password) > 0) and (len(username) > 0):
            #Tweet that you enjoy a song
            # this creates a password manager
            passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
            
            # because we have put None at the start it will always
            # use this username/password combination for  urls
            # for which `theurl` is a super-url
            passman.add_password(None, TWITTER_UPDATE, username, password)
            
            # create the AuthHandler
            authhandler = urllib2.HTTPBasicAuthHandler(passman)
    
            opener = urllib2.build_opener(authhandler)
    
            urllib2.install_opener(opener)
            # All calls to urllib2.urlopen will now use our handler
            # Make sure not to include the protocol in with the URL, or
            # HTTPPasswordMgrWithDefaultRealm will be very confused.
            # You must (of course) use it when fetching the page though.
            
            
            values = {'status' : twit_text}
            #write ur specific key/value pair
            #          'key2' : 'value2',
            #          'key3' : 'value3',
            #          }
    
            #headers = { 'X-Twitter-Client' : 'GrooveWalrus', 'X-Twitter-Client-URL' : 'http://groove-walrus.turnip-town-net', 'X-Twitter-Client-Version': '0.185' }
    
            try:
                data = urllib.urlencode(values)          
                req = urllib2.Request(TWITTER_UPDATE, data)#, headers)
                response = urllib2.urlopen(req)
                #the_page = response.read() 
                #print the_page 
            except Exception, detail: 
                print "Err ", detail 
            
            #pagehandle = urllib2.urlopen(theurl)
            # authentication is now handled automatically for us
            self.GetHomeTimeline()
            xrc.XRCCTRL(self, 'm_notebook1').SetSelection(0)
        else:
            self.ErrorMessage()
            
           
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
class PubSubReceiver(object):
  def __init__(self):
    # here we connect to a signal called 'object.added'
    # we use dotted notation for more specialized topics
    # but you can use tuples too
    pub.subscribe(self.__onObjectAdded, 'main.playback')

  def __onObjectAdded(self, message):
    # data passed with your message is put in message.data.
    # Any object can be passed to subscribers this way.
    print message.data
    return message.data
