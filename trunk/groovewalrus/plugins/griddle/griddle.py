"""
GrooveWalrus: Griddle Plug-in 
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
import wx.grid as gridlib
#from main_utils.read_write_xml import xml_utils
import sys, os
import sqlite3
from main_utils import local_songs
from main_utils import system_files

#SYSLOC = os.getcwd()
RESFILE = os.path.join(os.getcwd(), 'plugins','griddle') + os.sep + "layout_griddle.xml"
FILEDB = system_files.GetDirectories(None).DatabaseLocation()
MAIN_PLAYLIST = system_files.GetDirectories(None).DataDirectory() + os.sep + "playlist.xspf"

class MainPanel(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, "griddle", size=(650,400), style=wx.FRAME_SHAPED) #STAY_ON_TOP)        
        self.parent = parent
        
        # XML Resources can be loaded from a file like this:
        res = xrc.XmlResource(RESFILE)

        # Now create a panel from the resource data
        panel = res.LoadPanel(self, "m_pa_plugin_griddle")

        # control references --------------------        
        #header for dragging and moving
        self.st_griddle_header = xrc.XRCCTRL(self, 'm_st_griddle_header')
        self.pa_griddle_panel = xrc.XRCCTRL(self, 'm_pa_griddle_panel')
        self.bm_griddle_close = xrc.XRCCTRL(self, 'm_bm_griddle_close')        
        self.st_griddle_selected = xrc.XRCCTRL(self, 'm_st_griddle_selected')
        
        self.grid = HugeTableGrid(self.pa_griddle_panel, self, self.parent)
        
        # bindings ----------------
        self.bm_griddle_close.Bind(wx.EVT_LEFT_UP, self.CloseMe)
        self.Bind(wx.EVT_BUTTON, self.OnRefreshClick, id=xrc.XRCID('m_bu_griddle_refresh'))
        
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self.st_griddle_header.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.st_griddle_header.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.st_griddle_header.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.st_griddle_header.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)       
        
        # set layout --------------
        grid_sizer = wx.BoxSizer(wx.VERTICAL)
        grid_sizer.Add(self.grid, 1, wx.EXPAND|wx.ALL, 5)
        self.pa_griddle_panel.SetSizer(grid_sizer)        
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel, 1, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        #self.LoadSetings()
        
        
    def CloseMe(self, event=None):
        self.Destroy()
        
    def OnRefreshClick (self, event):
        self.grid.GetPlayed()
        self.grid.ForceRefresh()
      
                           
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
        #self.Destroy()
        
        
#SELECT music_id FROM m_tracks 
#INNER JOIN m_playcount ON 
#m_playcount.track_id = m_tracks.track_id 
#WHERE music_id <> 0 
#ORDER BY music_id
        
#---------------------------------------------------------------------------          
ROW_WIDTH = 50

class HugeTable(gridlib.PyGridTableBase):
    def __init__(self, parent):
        self.parent = parent
        self.parent.GetPlayed()
        gridlib.PyGridTableBase.__init__(self)
        #self.SetDefaultCellBackgroundColour("sea green")
        self.more=gridlib.GridCellAttr()
        self.more.SetBackgroundColour("#1b6f0d")
        self.less=gridlib.GridCellAttr()
        self.less.SetBackgroundColour("#51b741")
        self.empty=gridlib.GridCellAttr()
        self.empty.SetBackgroundColour("black")
        
        
    def GetAttr(self, row, col, kind):
        song_id = (row * ROW_WIDTH) + (col + 1)
        #print song_id

        #try:
        if song_id in self.parent.played_dict:
            if self.parent.played_dict[song_id] > 1:
                # played more than once
                attr = self.more
            else:
                attr = self.less
            attr.IncRef()
            return attr
        elif song_id > self.song_count:
            attr = self.empty
            attr.IncRef()
            return attr
        else:
            pass
    
    # This is all it takes to make a custom data table to plug into a
    # wxGrid.  There are many more methods that can be overridden, but
    # the ones shown below are the required ones.  This table simply
    # provides strings containing the row and column values.
    
    
    def GetSongCount(self):
        # get total local songs
        conn = sqlite3.connect(FILEDB)
        c = conn.cursor()
        t = "SELECT COUNT(*) as rcount FROM m_files"
        c.execute(t)
        h = c.fetchall()
        c.close()
        self.song_count = h[0][0]
        return(h[0][0])
        

    
    def GetNumberRows(self):
        rows = self.GetSongCount() / ROW_WIDTH
        if ((self.GetSongCount() % ROW_WIDTH) <> 0) | (self.GetSongCount() < ROW_WIDTH):
            rows = rows + 1
        return(rows)
        
    def GetNumberCols(self):        
        return(ROW_WIDTH)
        
    def IsEmptyCell(self, row, col):
        return False
        
    def GetValue(self, row, col):
        #return str( (row, col) )
        ret = ''
        return(ret)
        
    def SetValue(self, row, col, value):
        pass #self.log.write('SetValue(%d, %d, "%s") ignored.\n' % (row, col, value))
        
#---------------------------------------------------------------------------
class HugeTableGrid(gridlib.Grid):
    def __init__(self, parent, grandparent, main):
        gridlib.Grid.__init__(self, parent, -1)
        self.parent = parent
        self.main = main
        self.selected = 'Deselected'
        self.grandparent = grandparent
        #self.SetDefaultCellBackgroundColour("sea green")
        self.SetColLabelSize(0)
        self.SetRowLabelSize(0)
        self.SetDefaultColSize(10)
        self.SetDefaultRowSize(10)
        self.EnableEditing(False)
        self.EnableDragRowSize(False)
        self.EnableDragColSize(False)
        
        
        table = HugeTable(self)
        # The second parameter means that the grid is to take ownership of the
        # table and will destroy it when done.  Otherwise you would need to keep
        # a reference to it and call it's Destroy method later.
        self.SetTable(table, True)
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_CLICK, self.OnClick)
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_DCLICK, self.OnDoubleClick)
        self.Bind(gridlib.EVT_GRID_RANGE_SELECT, self.OnRangeSelect)
        self.Bind(gridlib.EVT_GRID_CELL_RIGHT_CLICK, self.OnRightClick)  
        
    def OnClick(self, event):
        # get the selected song
        row = event.GetRow()
        col = event.GetCol()
        music_id = (row * ROW_WIDTH) + (col + 1)
        (artist, song, file_name, folder_name, folder_path) = self.GetFileName(music_id)
        self.grandparent.st_griddle_selected.SetLabel(artist + ' - ' + song)
        event.Skip()
        
    def GetPlayed(self):
        # get last songs played
        conn = sqlite3.connect(FILEDB)
        c = conn.cursor()
        t = "SELECT music_id, local_playcount FROM m_tracks INNER JOIN m_playcount ON m_playcount.track_id = m_tracks.track_id WHERE music_id <> 0 ORDER BY music_id"
        c.execute(t)
        h = c.fetchall()
        counter = 0
        self.played_dict = {}
        for x in h:
            self.played_dict[x[0]] = x[1]
        c.close()
        #return(self.played_dict)
                
    def GetFileName(self, music_id):
        conn = sqlite3.connect(FILEDB)
        c = conn.cursor()
        t = "SELECT folder_path, folder_name, file_name FROM m_files WHERE music_id = " + str(music_id)
        c.execute(t)
        artist = ''
        song = ''
        file_name = ''
        folder_name = ''
        folder_path = ''
        h = c.fetchall()
        for x in h:
            file_name = x[2]
            folder_name= x[1]
            folder_path= x[0]
            artist = local_songs.GetMp3Artist(folder_path + '/' + folder_name + '/' + file_name)
            song = local_songs.GetMp3Title(folder_path + '/' + folder_name + '/' + file_name)
        c.close()
        return(artist, song, file_name, folder_name, folder_path)
        
    def OnDoubleClick(self, event):
        # get the selected song
        row = event.GetRow()
        col = event.GetCol()
        music_id = (row * ROW_WIDTH) + (col + 1)
        (artist, song, file_name, folder_name, folder_path) = self.GetFileName(music_id)
        self.main.SearchOrPlaylist(artist, song, '', folder_path + '/' + folder_name + '/' + file_name)
        
    def OnRangeSelect(self, evt):
        # get the range of selected items
        if evt.Selecting():
            self.selected = 'Selected'
            self.top_yx = evt.GetTopLeftCoords()
            self.bot_yx = evt.GetBottomRightCoords()

            
        else:
            self.selected = 'Deselected'      
        evt.Skip()
        
    def OnRightClick(self, event):
        # display a menu for playlist adding
        if self.selected == 'Selected':
            # make a menu
            ID_PLAYLIST = 1
            ID_CLEAR = 2
            menu = wx.Menu()
            menu.Append(ID_PLAYLIST, "Add to Playlist")
            menu.AppendSeparator()
            menu.Append(ID_CLEAR, "Clear Playlist")
            wx.EVT_MENU(self, ID_PLAYLIST, self.AddToPlaylist)
            wx.EVT_MENU(self, ID_CLEAR, self.main.OnClearPlaylistClick)       
            self.PopupMenu(menu)
            menu.Destroy()
        
    def AddToPlaylist(self, event):
        current_count = self.main.lc_playlist.GetItemCount()
        #print val
        for y in range(self.top_yx[1], self.bot_yx[1] + 1):                
            for x in range(self.top_yx[0], self.bot_yx[0] + 1):
                music_id = (x * ROW_WIDTH) + (y + 1)
                (artist, song, file_name, folder_name, folder_path) = self.GetFileName(music_id)
                self.main.SetPlaylistItem(current_count, artist, song, '', folder_path + '/' + folder_name + '/' + file_name)
                current_count = current_count + 1
        #save the playlist
        self.main.SavePlaylist(MAIN_PLAYLIST)

                    
#---------------------------------------------------------------------------
  
