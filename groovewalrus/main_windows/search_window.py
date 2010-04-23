#!/bin/env python
"""
GrooveWalrus: Search Window 
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
from main_utils import tinysong
from main_utils import local_songs
#from main_utils import drag_and_drop

import sys, os
SYSLOC = os.path.abspath(os.path.dirname(sys.argv[0]))

SEARCH_RESFILE = SYSLOC + '\\layout_search.xml'

class SearchWindow(wx.Dialog):
    """Search Window for searching"""
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, "Search", style=wx.FRAME_SHAPED) #STAY_ON_TOP)#wx.FRAME_SHAPED)
        self.parent = parent
        
        # XML Resources can be loaded from a file like this:
        res = xrc.XmlResource(SEARCH_RESFILE)

        # Now create a panel from the resource data
        panel = res.LoadPanel(self, "m_pa_search")

        # control references --------------------
        self.tc_search_text = xrc.XRCCTRL(self, 'm_tc_search_text')
        self.st_search_header = xrc.XRCCTRL(self, 'm_st_search_header')
        self.bm_search_close = xrc.XRCCTRL(self, 'm_bm_search_close')
        self.cb_search_local = xrc.XRCCTRL(self, 'm_cb_search_local')
        #self.cb_search_noid = xrc.XRCCTRL(self, 'm_cb_search_noid')
        #self.st_search_header = xrc.XRCCTRL(self, 'm_st_search_header')
        # and do the layout
        
        
        # list control, column setup ------------
        # search is subclassed to draglist in the xrc
        self.lc_search = xrc.XRCCTRL(self, 'm_lc_search')
        self.lc_search.InsertColumn(0,"Artist")
        self.lc_search.InsertColumn(1,"Song")
        self.lc_search.InsertColumn(2,"Album")
        self.lc_search.InsertColumn(3,"Id")
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnSearchListClick, self.lc_search)

        # bindings ----------------
        self.Bind(wx.EVT_BUTTON, self.OnSearchClick, id=xrc.XRCID('m_bb_search_button'))
        self.Bind(wx.EVT_BUTTON, self.OnSearchListClick, id=xrc.XRCID('m_bb_search_add'))
        self.Bind(wx.EVT_BUTTON, self.OnSearchClear, id=xrc.XRCID('m_bb_search_clear'))
        self.Bind(wx.EVT_TEXT_ENTER, self.OnSearchClick, self.tc_search_text)
        self.bm_search_close.Bind(wx.EVT_LEFT_UP, self.hide_me)
        
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self.st_search_header.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.st_search_header.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.st_search_header.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.st_search_header.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
                
        # set layout --------------
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel, 1, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        
#----------------------------------------------------------------------
                
    def show_me(self):
        # show the window
        #self.CenterOnScreen()
        #self.ShowModal() # Shows it        
        #self.Destroy() # finally destroy it when finished.
        #self.Disaply(True)
        self.MoveMe()
        self.Show(True) # Shows it        
        
    def MoveMe(self, event=None):
        # show the window
        ps = self.parent.GetSize()
        pp = self.parent.GetScreenPosition()
        ss = self.GetSize()        
        xn = pp[0] + (ps[0] - ss[0])
        yn = pp[1] # + (ps[1] - ss[1])
        self.SetPosition((xn, yn))
        self.SetSize((ss[0], ps[1]))
        
    def SetValue(self, query_string):
        # set search value
        self.tc_search_text.SetValue(query_string)
        
    def OnSearchClear(self, event):
        # set search value
        self.tc_search_text.SetValue('')
        
    def hide_me(self, event=None):
        # hide the window
        self.Show(False)

#----------------------------------------------------------------------        
    def OnSearchListClick(self, event):
        # get selected search relsult list item and add to playlist
        #val = event.GetIndex()
        val = self.lc_search.GetFirstSelected()
        total = self.lc_search.GetSelectedItemCount()
        current_count = self.parent.lc_playlist.GetItemCount()
        #print val
        if val >= 0:
            artist = self.lc_search.GetItem(val, 0).GetText()
            song = self.lc_search.GetItem(val, 1).GetText()
            album = self.lc_search.GetItem(val, 2).GetText()
            url = self.lc_search.GetItem(val, 3).GetText()
            self.parent.SetPlaylistItem(current_count, artist, song, album, url)
            current_select = val
            if total > 1:
                for x in range(1, self.lc_search.GetSelectedItemCount()):
                    current_select = self.lc_search.GetNextSelected(current_select)
                    artist = self.lc_search.GetItem(current_select, 0).GetText()
                    song = self.lc_search.GetItem(current_select, 1).GetText()
                    album = self.lc_search.GetItem(current_select, 2).GetText()
                    url = self.lc_search.GetItem(current_select, 3).GetText()
                    self.parent.SetPlaylistItem(current_count + x, artist, song, album, url)
        
            # save playlist file
            self.parent.SavePlaylist()
        
#----------------------------------------------------------------------
    def OnSearchClick(self, event):
        # search field, then search
        query_string = self.tc_search_text.GetValue()
        self.SearchIt(query_string)
        #self.nb_main.SetSelection(0)
        #self.search_window.show_me()
        
    def SearchIt(self, query_string):
        # search field, then search
        if len(query_string) > 0:
            if self.cb_search_local.GetValue() == True:
                query_results = local_songs.DbFuncs().GetResultsArray(query_string, 40)
                self.FillSearchListLocal(query_results, query_string);
            else:
                query_results = tinysong.Tsong().get_search_results(query_string)
                self.FillSearchList(query_results);            
            
    def FillSearchList(self, query_results):
        # search field, then search
        counter = 0
        # calc how many time to run through the loop, based on 8 items per result
        #times_to_run = divmod(len(query_results), 8)[0]
        #print times_to_run
        self.lc_search.DeleteAllItems()
        for x in query_results:
            if len(x) > 0:
                #print counter
                #split_array = x.split('; ')
                if len(x) > 5:
                    play_url = x['SongID']#split_array[1]
                    # http://listen.grooveshark.com/songWidget.swf?hostname=cowbell.grooveshark.com&songID=13721223&style=metal&p=0

                    # artist
                    index = self.lc_search.InsertStringItem(counter, x['ArtistName'])
                    # title
                    self.lc_search.SetStringItem(counter, 1, x['SongName'])
                    #album
                    self.lc_search.SetStringItem(counter, 2, x['AlbumName'])
                    if self.parent.cb_options_noid.GetValue() == False:
                        self.lc_search.SetStringItem(counter, 3, play_url)
                else:
                    index = self.lc_search.InsertStringItem(counter, 'No Results')
                    # title
                    self.lc_search.SetStringItem(counter, 1, 'Found')

                counter = counter + 1
        self.ResizeColumns()
        
    def FillSearchListLocal(self, query_results, query):
        # search field, then search
        counter = 0
        # calc how many time to run through the loop, based on 8 items per result
        #times_to_run = divmod(len(query_results), 8)[0]
        #print times_to_run
        self.lc_search.DeleteAllItems()
        for x in query_results:
            if len(x) > 0:
                
                found_exact_match = False                
                # put results that match exactly at the top of the list
                if query.upper() == (x[0] + ' ' + x[1]).upper():
                    found_exact_match = True
                        
                if found_exact_match == True:    
                    #add artist, song, album, path, add at top
                    index = self.lc_search.InsertStringItem(0, x[0])
                    self.lc_search.SetStringItem(0, 1, x[1])
                    self.lc_search.SetStringItem(0, 2, x[2])
                    if self.parent.cb_options_noid.GetValue() == False:
                        self.lc_search.SetStringItem(0, 3, x[3])

                else:
                    #add artist, song, album, path
                    index = self.lc_search.InsertStringItem(counter, x[0])
                    self.lc_search.SetStringItem(counter, 1, x[1])
                    self.lc_search.SetStringItem(counter, 2, x[2])
                    if self.parent.cb_options_noid.GetValue() == False:
                        self.lc_search.SetStringItem(counter, 3, x[3])

                counter = counter + 1
        self.ResizeColumns()
                
    def ResizeColumns(self):
        # resize columns
        self.lc_search.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.lc_search.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        self.lc_search.SetColumnWidth(2, wx.LIST_AUTOSIZE)
        self.lc_search.SetColumnWidth(3, wx.LIST_AUTOSIZE)
        
        
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
            #try:
            #    self.popup.IsShown()
            #except AttributeError:
            #    pass
            #else:
            #    if (self.popup.IsShown()):
            #        pPos = (self.wPos.x + (dPos.x - self.ldPos.x),34)
             #       self.popup.Move(pPos)

    def OnMouseLeftUp(self, evt):
        try:
            self.ReleaseMouse()
        except wx._core.PyAssertionError:
            pass

    def OnRightUp(self, evt):
        self.hide_me()
        #self..Destroy()
        
# --------------------------------------------------------- 
