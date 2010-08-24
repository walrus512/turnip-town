"""
GrooveWalrus: List Sifter Tab
Copyright (C) 2010
11y3y3y3y43@gmail.com
gardener@turnip-town.net
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
import sqlite3
from main_utils import system_files
from main_utils import download_feed
from main_utils import local_songs

#columns
C_RATING = 0
C_ARTIST = 1
C_SONG = 2
C_ALBUM = 3
C_ID = 4
C_TIME = 5

class ListSifterTab(wx.ScrolledWindow):
    def __init__(self, parent):
        self.parent = parent
        
        # sifter
        self.tc_sift_pre =          xrc.XRCCTRL(self.parent, 'm_tc_sift_pre')
        self.tc_sift_seperator =    xrc.XRCCTRL(self.parent, 'm_tc_sift_seperator')
        self.tc_sift_post =         xrc.XRCCTRL(self.parent, 'm_tc_sift_post')
        self.lc_sift_rss =          xrc.XRCCTRL(self.parent, 'm_lc_sift_rss')
        self.tc_sift_rss_url =      xrc.XRCCTRL(self.parent, 'm_tc_sift_rss_url')
        self.ch_sift_rss =          xrc.XRCCTRL(self.parent, 'm_ch_sift_rss')
        self.tc_sift_rawlist =      xrc.XRCCTRL(self.parent, 'm_tc_sift_rawlist')
        self.nb_sift_rss =          xrc.XRCCTRL(self.parent, 'm_nb_sift_rss')
        self.ch_sift_choice =       xrc.XRCCTRL(self.parent, 'm_ch_sift_choice')
               
        
        # list sifter: list control -------
        self.lc_sift =              xrc.XRCCTRL(self.parent, 'm_lc_sift')
        self.lc_sift.InsertColumn(0,"Rating")
        self.lc_sift.InsertColumn(1,"Artist")
        self.lc_sift.InsertColumn(2,"Song")
        self.parent.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnSiftDoubleClick, self.lc_sift)
        # wxMSW
        self.parent.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnSiftRightClick, self.lc_sift)
        # wxGTK
        self.lc_sift.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnSiftRightClick)
        self.lc_sift.Bind(wx.EVT_CHAR, self.parent.OnChar)
        
        # list sifter: rss list control ----
        self.lc_sift_rss =          xrc.XRCCTRL(self.parent, 'm_lc_sift_rss')
        self.lc_sift_rss.InsertColumn(0,"Feed Url")
        self.parent.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnRSSClick, self.lc_sift_rss)
        # wxMSW
        self.parent.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnRSSRightClick, self.lc_sift_rss)
        # wxGTK
        self.lc_sift_rss.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnRSSRightClick)
        
        
        #list sifter
        self.parent.Bind(wx.EVT_BUTTON, self.OnSiftClick, id=xrc.XRCID('m_bu_sift_sift'))
        self.parent.Bind(wx.EVT_BUTTON, self.OnSiftRSS, id=xrc.XRCID('m_bu_sift_rss'))
        self.parent.Bind(wx.EVT_BUTTON, self.OnSaveRSSClick, id=xrc.XRCID('m_bb_sift_rss_save'))
        self.parent.Bind(wx.EVT_BUTTON, self.OnSiftURLClear, id=xrc.XRCID('m_bb_sift_url_clear'))
        
        self.parent.Bind(wx.EVT_BUTTON, self.OnAutoGenerateSiftPlayist, id=xrc.XRCID('m_bb_sift_plize'))
        self.parent.Bind(wx.EVT_BUTTON, self.OnSiftDoubleClick, id=xrc.XRCID('m_bb_sift_add'))
        
        
# sifter  -------------------------------------------------- 
  
    def OnSiftClick(self, event):
        # check to see if there's stuff in the 'list' text control
        # split pre-split and rest
        # next split that with seperator
        # add the results to the list control
        sift_pre = self.tc_sift_pre.GetValue()
        sift_seperator = self.tc_sift_seperator.GetValue()
        sift_post = self.tc_sift_post.GetValue()
        s_choice = self.ch_sift_choice.GetSelection()
        #print s_choice
        # check if something is selected
        # cycle through each 'list' line
        text_glob = self.tc_sift_rawlist.GetValue().split('\n')
        
        self.lc_sift.DeleteAllItems()
        counter = 0;
        
        # use '[#]char' to skip to the seperator ex [2]. is second .
        split_number = 1
        if len(sift_pre) > 3:
            if (sift_pre[0] == '[') & (sift_pre[2] == ']') & (sift_pre[1].isdigit()):
                print 'boo'
                split_number = int(sift_pre[1])
                sift_pre = sift_pre[3:]
        
        if (len(text_glob) > 0) & (sift_seperator != ''):
            #print len(text_glob)
            for x in text_glob:
                if len(sift_pre) > 0:
                    part_one = x.split(sift_pre, split_number)[-1]
                else:
                    part_one = x
                part_two = part_one.split(sift_seperator, 1)
                artist = part_two[0]
                if len(part_two) > 1:
                    song = part_two[1]
                    if sift_post != '':
                        post_song = song.rsplit(sift_post, 1)
                        song = post_song[0]
                else:
                    song = ''
                                    
                # add to list control
                if s_choice == 0:
                    if (artist != '') & (song != ''):
                        self.lc_sift.InsertStringItem(counter, '')
                        self.lc_sift.SetStringItem(counter, C_ARTIST, artist.strip())
                        self.lc_sift.SetStringItem(counter, C_SONG, song.strip().replace('"', ''))
                        counter = counter + 1
                else:
                    if (artist != '') & (song != ''):
                        self.lc_sift.InsertStringItem(counter, '')
                        self.lc_sift.SetStringItem(counter, C_ARTIST, song.strip().replace('"', ''))
                        self.lc_sift.SetStringItem(counter, C_SONG, artist.strip())
                        counter = counter + 1
            
            self.lc_sift.SetColumnWidth(C_RATING, 0)   
            self.lc_sift.SetColumnWidth(C_ARTIST, 120)
            self.lc_sift.SetColumnWidth(C_SONG, wx.LIST_AUTOSIZE)
            #print self.lc_sift.GetItemCount()
            
    def OnRSSClick(self, event):
        # load selected rss feed
        val = self.lc_sift_rss.GetFirstSelected()
        if val != None:
            feed = self.lc_sift_rss.GetItem(val, 0).GetText()
            self.tc_sift_rss_url.SetValue(feed)
            
    def OnRSSRightClick(self, event):
        # show menu for deleting the rss feed
        val = self.lc_sift_rss.GetFirstSelected()
        if val != -1:
            if (self.lc_sift_rss.GetItem(val, 0).GetText() != ''):    
                # make a menu
                ID_DELETE = 1
                menu = wx.Menu()
                menu.Append(ID_DELETE, "Delete Feed")
                wx.EVT_MENU(self.parent, ID_DELETE, self.OnDeleteRSSClick)       
                self.parent.PopupMenu(menu)
                menu.Destroy()
                
    def OnDeleteRSSClick(self, event):
        # remove the rss feed from the database
        val = self.lc_sift_rss.GetFirstSelected()
        feed = self.lc_sift_rss.GetItem(val, 0).GetText()
        local_songs.DbFuncs().RemoveFeedRow(feed)   
        self.LoadRSSFeeds()
        
    def OnSaveRSSClick(self, event):
        # save the rss feed to the database
        feed = self.tc_sift_rss_url.GetValue()
        if feed !='':
            self.SaveRSSFeed(feed)            
        
    def SaveRSSFeed(self, feed_name):
        #save a feed url to the db               
        local_songs.DbFuncs().InsertFeedData(feed_name)
        self.LoadRSSFeeds()
        
    def LoadRSSFeeds(self):
        self.lc_sift_rss.DeleteAllItems()
        #populate rss listctrl
        FILEDB = system_files.GetDirectories(None).DatabaseLocation()
        conn = sqlite3.connect(FILEDB)
        c = conn.cursor()
        query = "SELECT feed_url FROM m_feeds ORDER BY feed_url"
        
        c.execute(query)
        h = c.fetchall()
        counter = 0
        for x in h:
            #print x
            try:
                index = self.lc_sift_rss.InsertStringItem(counter, x[counter])               
            except TypeError, err:
                print 'Type error: ' + str(err)
                pass
        c.close()
        self.lc_sift_rss.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        
    def OnSiftRSS(self, event):
        # load the rss file and pass to the list sifter
        if (self.tc_sift_rss_url.GetValue() != ''):
            #fetch rss feed
            rss_feed = download_feed.GetRSSFeed(self.tc_sift_rss_url.GetValue())
            #pass to pastebox
            feed_out = ''
            for x in rss_feed:
                feed_out = feed_out + x + '\n'
            self.tc_sift_rawlist.SetValue(feed_out)
            #switch to the textbox tab
            self.nb_sift_rss.SetSelection(0)
            
    def OnSiftURLClear(self, event):
        #clear the url field
        self.tc_sift_rss_url.SetValue('')
             
    def OnSiftRightClick(self, event):
        val = self.lc_sift.GetFirstSelected()
        if val != -1:
            if (self.lc_sift.GetItem(val, C_ARTIST).GetText() != '') & (self.lc_sift.GetItem(val, C_SONG).GetText() != ''):    
                # make a menu
                ID_PLAYLIST = 1
                ID_CLEAR = 2
                menu = wx.Menu()
                menu.Append(ID_PLAYLIST, "Add to Playlist")
                menu.AppendSeparator()
                menu.Append(ID_CLEAR, "Clear Playlist")
                wx.EVT_MENU(self.parent, ID_PLAYLIST, self.SiftAddPlaylist)
                wx.EVT_MENU(self.parent, ID_CLEAR, self.parent.OnClearPlaylistClick)       
                self.parent.PopupMenu(menu)
                menu.Destroy()
        
    # playlist adding ---------------
                
    def OnAutoGenerateSiftPlayist(self, event):
        """ add all the list items to the playlist """
        self.parent.AddAll(self.lc_sift)
        
    def OnSiftDoubleClick(self, event):
        """ add the selected list items to the playlist """
        self.parent.AddSelected(self.lc_sift)