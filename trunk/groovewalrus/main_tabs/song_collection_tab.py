"""
GrooveWalrus: Song Collection Tab
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
import os
from main_utils import system_files
from main_utils import local_songs
from main_windows import song_collection

class SongCollectionTab(wx.ScrolledWindow):
    def __init__(self, parent):
        self.parent = parent
        
        # song collection controls
        self.tc_scol_song = xrc.XRCCTRL(self.parent, 'm_tc_scol_song')
        self.tc_scol_folder = xrc.XRCCTRL(self.parent, 'm_tc_scol_folder')
        self.rb_scol_folder = xrc.XRCCTRL(self.parent, 'm_rb_scol_folder')
        self.rb_scol_file = xrc.XRCCTRL(self.parent, 'm_rb_scol_file')
        
        
        self.tr_scol_folders = xrc.XRCCTRL(self.parent, 'm_tr_scol_folders')
        self.parent.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivate, self.tr_scol_folders)
        #self.tl_scol_folder = xrc.XRCCTRL(self.parent, 'm_tl_scol_folder')
        
        #treelist control
        #self.tl_scol_folder.SetWindowStyleFlag(wx.TR_FULL_ROW_HIGHLIGHT)#wx.TR_DEFAULT_STYLE|wx.TR_FULL_ROW_HIGHLIGHT) #|wx.SIMPLE_BORDER
        # create some columns
        #self.tl_scol_folder.AddColumn("Main column")
        #self.tl_scol_folder.AddColumn("Column 1")
        #self.tl_scol_folder.AddColumn("Column 2")
        #self.tl_scol_folder.SetMainColumn(0) # the one with the tree in it...
        #self.tl_scol_folder.SetColumnWidth(0, 575)

        
        
        # list control
        self.lc_scol_col = xrc.XRCCTRL(self.parent, 'm_lc_scol_col')
        self.lc_scol_col.InsertColumn(0,"Id")
        self.lc_scol_col.InsertColumn(1,"File")
        self.lc_scol_col.InsertColumn(2,"Folder")
        self.lc_scol_col.InsertColumn(3,"Location")
        
        self.lc_scol_col.SetColumnWidth(0, 50)
        self.lc_scol_col.SetColumnWidth(1, 175)
        self.lc_scol_col.SetColumnWidth(2, 150)
        self.lc_scol_col.SetColumnWidth(3, 190)
        self.lc_scol_col.SetItemCount(local_songs.DbFuncs().GetCountAndLast()[0])
        # wxMSW
        self.parent.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnScolRightClick, self.lc_scol_col)
        # wxGTK
        self.lc_scol_col.Bind(wx.EVT_RIGHT_UP, self.OnScolRightClick)
        self.parent.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.ScolAddPlaylist, self.lc_scol_col)
        
        
        #bindings
        self.tc_scol_song.Bind(wx.EVT_TEXT, self.OnSColSongText)
        self.tc_scol_folder.Bind(wx.EVT_TEXT, self.OnSColFolderText)
        self.parent.Bind(wx.EVT_RADIOBUTTON, self.OnSColRadio, self.rb_scol_folder)
        self.parent.Bind(wx.EVT_RADIOBUTTON, self.OnSColRadio, self.rb_scol_file)        
        self.parent.Bind(wx.EVT_BUTTON, self.OnSColAddClick, id=xrc.XRCID('m_bb_scol_add'))
        self.parent.Bind(wx.EVT_BUTTON, self.OnSColDeleteClick, id=xrc.XRCID('m_bb_scol_delete'))
        self.parent.Bind(wx.EVT_BUTTON, self.ScolAddPlaylist, id=xrc.XRCID('m_bb_scol_playlist'))
        self.parent.Bind(wx.EVT_BUTTON, self.OnSColClearClick, id=xrc.XRCID('m_bb_scol_clear'))
        self.parent.Bind(wx.EVT_BUTTON, self.OnSColClearClickFolder, id=xrc.XRCID('m_bb_scol_clear_folder'))
        
        self.FillFolderList()
        
# --------------------------------------------------------- 
# song collection -----------------------------------------  
    def OnSColAddClick(self, event):
        # show song db window
        #song_db_window = local_songs.SongDBWindow(self)
        song_db_window = song_collection.SongDBWindow(self.parent)
        song_db_window.show_me()
        
    def OnSColDeleteClick(self, event):
        # show song db window        
        # remove slected list item
        val = self.lc_scol_col.GetFirstSelected()
        # iterate over all selected items and delete
        for x in range(val, val + self.lc_scol_col.GetSelectedItemCount()):
            #print 'dete - ' + str(val)
            #self.lc_playlist.DeleteItem(val)
            #get the id and remove from db
            row_id = self.lc_scol_col.GetItem(x, 0).GetText()
            local_songs.DbFuncs().RemoveRow(row_id)
            #self.lc_scol_col.DeleteItem(self.lc_scol_col.GetFirstSelected())
        self.RefreshSCol()
        
    def RefreshSCol(self, event=None):
        # refresh the song collection list control        
        self.lc_scol_col.DeleteAllItems()
        self.lc_scol_col.SetItemCount(local_songs.DbFuncs().GetCountAndLast()[0])
        
    def OnScolRightClick(self, event):        
        # make a menu
        ID_PLAYLIST = 1
        ID_CLEAR = 2
        #ID_FAVES = 3
        
        menu = wx.Menu()
        menu.Append(ID_PLAYLIST, "Add to Playlist")
        menu.AppendSeparator()
        menu.Append(ID_CLEAR, "Clear Playlist")       
        
        wx.EVT_MENU(self, ID_PLAYLIST, self.ScolAddPlaylist)
        wx.EVT_MENU(self, ID_CLEAR, self.OnClearPlaylistClick)
        
        self.PopupMenu(menu)
        menu.Destroy()
        
    def ScolAddPlaylist(self, event):
        self.parent.BackupList()
        # cycle through selected
        val = self.lc_scol_col.GetFirstSelected()
        # iterate over all selected items and delete
        #self.CheckClear()
        #check for file or folder
        if val != -1:
            if self.lc_scol_col.GetItem(val, 0).GetText() == ' ':
                #it's just a folder, first item is ' '  not ''
                #pen folder, cycle through mp3 file adding to playlist
                folder = self.lc_scol_col.GetItem(val, 2).GetText()
                folder_arr = local_songs.DbFuncs().GetResultsArray(folder, 100, True, 2)
                for x in range(0, len(folder_arr)):
                    self.ScolFileAdd(folder_arr[x][4])
            else:
                # it's a file
                for x in range(val, val + self.lc_scol_col.GetSelectedItemCount()):
                    mfile = self.lc_scol_col.GetItem(x, 1).GetText()
                    mfolder = self.lc_scol_col.GetItem(x, 2).GetText()
                    mpath = self.lc_scol_col.GetItem(x, 3).GetText()
                    if mfolder == ' ':
                        self.ScolFileAdd(mpath + '/' + mfile)
                    else:
                        self.ScolFileAdd(mpath + '/' + mfolder + '/' + mfile)

            
    def ScolFileAdd(self, file_name):
        # copy the faves list to the playlist        
        insert_at = self.parent.lc_playlist.GetItemCount()
        
        artist = local_songs.GetMp3Artist(file_name)
        song = local_songs.GetMp3Title(file_name)
        album = local_songs.GetMp3Album(file_name)
        song_id = file_name.replace(os.sep, '/')
        duration = self.parent.ConvertTimeFormated(local_songs.GetMp3Length(file_name))
        self.parent.SetPlaylistItem(insert_at, artist, song, album, song_id, duration)
        #save the playlist
        self.parent.SavePlaylist(self.parent.main_playlist_location)
        # switch tabs
        #self.nb_main.SetSelection(NB_PLAYLIST)
        
    def OnSColClearClick(self, event):
        # clear album search field
        self.tc_scol_song.Clear()
        #self.tc_scol_folder.Clear()
        
    def OnSColClearClickFolder(self, event):
        # clear search field
        self.tc_scol_folder.Clear()
      
    def OnSColSongText(self, event):
        # search local db for matches
        if self.rb_scol_file.GetValue() == True:
            qtype = 'file'
            self.SCAdjustColumns('files')
        else:
            qtype = 'folder'
            self.SCAdjustColumns('folders')
        query = self.tc_scol_song.GetValue()
        self.lc_scol_col.SetQuery(query, qtype)
        
    def OnSColRadio(self, event):
        self.OnSColSongText(None)
        
    def SCAdjustColumns(self, col_type):
        if col_type == 'files':        
            self.lc_scol_col.SetColumnWidth(0, 50)
            self.lc_scol_col.SetColumnWidth(1, 175)
            self.lc_scol_col.SetColumnWidth(2, 150)
            self.lc_scol_col.SetColumnWidth(3, 190)            
        else:
            self.lc_scol_col.SetColumnWidth(0, 0)
            self.lc_scol_col.SetColumnWidth(1, 0)
            self.lc_scol_col.SetColumnWidth(2, 520)
            self.lc_scol_col.SetColumnWidth(3, 0)
            
    def FillFolderList(self, query=None):
        #fills the treelist control with folders and songs
        FILEDB = system_files.GetDirectories(None).DatabaseLocation()
        conn = sqlite3.connect(FILEDB)
        # for unicode/crazy text errors
        conn.text_factory = str
        c = conn.cursor()
        if query == None:
            #default query            
            query = "SELECT DISTINCT folder_name, folder_path FROM m_files ORDER BY folder_name" #LIMIT 100"
            #print query
        c.execute(query)
        h = c.fetchall()
            
        #print h

        self.root = self.tr_scol_folders.AddRoot("Folders")
        #self.tr_scol_folders.SetItemText(self.root, "Artist")
        #self.tl_scol_folder.SetItemText(self.root, "col 2 root", 2)
        
        
        old_folder_name = 'start'
        for x in range(len(h)):
            folder_name = h[x][0]
            if folder_name == '':
                folder_name = '(root)'
           
            disp = str(x)
            if old_folder_name != folder_name:
                child = self.tr_scol_folders.AppendItem(self.root, folder_name)
                old_folder_name = folder_name
                #self.tl_scol_folder.SetItemText(child, folder_name, 1)
                #self.tl_scol_folder.SetItemText(child, txt + "(c2)", 2)
            
            #for y in range(5):                
                
            #song_name = h[x][0]
            #last = self.tr_scol_folders.AppendItem(child, song_name)
                #self.tl_scol_folder.SetItemText(last, txt + "(c1)", 1)
            #    self.tl_scol_folder.SetItemText(last, txt + "(c2)", 2)
            
    def OnActivate(self, event):
        #get the songs for the selected folder
        item = event.GetItem()
        folder_name = self.tr_scol_folders.GetItemText(item)
        if folder_name == '(root)':
            folder_name = ''
        FILEDB = system_files.GetDirectories(None).DatabaseLocation()
        conn = sqlite3.connect(FILEDB)
        # for unicode/crazy text errors
        conn.text_factory = str
        c = conn.cursor()
        
        query = "SELECT file_name FROM m_files WHERE folder_name = '" + folder_name + "' ORDER BY file_name" #LIMIT 100"
        
        c.execute(query)
        h = c.fetchall()
        self.tr_scol_folders.DeleteChildren(item)
        for x in h:
            self.tr_scol_folders.AppendItem(item, x[0])
        self.tr_scol_folders.Expand(item)
        
    def OnSColFolderText(self, event):
        # search local db for folder matches
        q_text = self.tc_scol_folder.GetValue()
        if xrc.XRCCTRL(self.parent, 'm_cb_scol_start_folder').GetValue() == True:
            query = "SELECT DISTINCT folder_name, folder_path FROM m_files WHERE folder_name LIKE '" + q_text + "%' ORDER BY folder_name" #LIMIT 100" 
        else:
            query = "SELECT DISTINCT folder_name, folder_path FROM m_files WHERE folder_name LIKE '%" + q_text + "%' ORDER BY folder_name" #LIMIT 100" 
        self.tr_scol_folders.DeleteAllItems()
        self.FillFolderList(query)