"""
GrooveWalrus: Favorites Tab
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
from main_controls import ratings_button
from main_utils import system_files
from main_utils import local_songs

class FavoritesTab(wx.ScrolledWindow):
    def __init__(self, parent):
        self.parent = parent

        # faves list control
        self.lc_faves = xrc.XRCCTRL(self.parent, 'm_lc_faves')
        self.lc_faves.InsertColumn(0,"Artist")
        self.lc_faves.InsertColumn(1,"Song")
        self.lc_faves.InsertColumn(2,"Album")
        self.lc_faves.InsertColumn(3,"Id")
        self.lc_faves.InsertColumn(4,"Time")        
        self.parent.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnFavesDoubleClick, self.lc_faves)
        # wxMSW
        self.parent.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnFavesRightClick, self.lc_faves)
        # wxGTK
        self.lc_faves.Bind(wx.EVT_RIGHT_UP, self.OnFavesRightClick)
        #self.lc_faves.Bind(wx.EVT_KEY_UP, self.OnDeleteClick)
        self.lc_faves.Bind(wx.EVT_LIST_COL_CLICK, self.OnFavesColClick)
        self.faves_sorter = [1,0,0,0,0]
        
        self.lc_faves.AssignImageList(self.parent.RateImageList(), wx.IMAGE_LIST_SMALL)        
        
        #faves
        ##self.parent.Bind(wx.EVT_BUTTON, self.RemoveFavesItem, id=xrc.XRCID('m_bb_faves_remove'))        
        self.parent.Bind(wx.EVT_BUTTON, self.OnFavesClick, id=xrc.XRCID('m_bb_faves'))
        self.parent.Bind(wx.EVT_BUTTON, self.FavesAddPlaylist, id=xrc.XRCID('m_bb_faves_playlist'))
        
        self.parent.Bind(wx.EVT_BUTTON, self.OnAutoGenerateFavesPlayist, id=xrc.XRCID('m_bb_faves_plize'))
        
# --------------------------------------------------------- 
# faves  -------------------------------------------------- 
  
    def OnFavesClick(self, event):
        # get current song and add to favourites list
        # this is not the same as clicking from the playlist
        
        music_id = self.parent.pmusic_id
        grooveshark_id = self.parent.pgroove_id
        artist = self.parent.partist
        song = self.parent.ptrack
        
        track_id = ratings_button.GetTrackId(artist, song, grooveshark_id, music_id)
        ratings_button.AddRating(self, track_id, 4)
        sk = self.parent.GenerateSessionKey2()
        ratings_button.LoveTrack(artist, song, sk)        
        
    def OnPlaylistFavesClick(self, event):
        # add a favorite (or many faves) from the right-click menu on the playlist
        val = self.parent.lc_playlist.GetFirstSelected()
        # check if something is selected
        need_love = True
        if val >= 0:
        #    current_count = (self.lc_faves.GetItemCount())
            for x in range(0, self.parent.lc_playlist.GetSelectedItemCount()):
                artist = self.parent.lc_playlist.GetItem(val, 0).GetText()
                song = self.parent.lc_playlist.GetItem(val, 1).GetText()
                grooveshark_id = ''
                music_id = ''
                
                the_id = self.parent.lc_playlist.GetItem(val, 1).GetText()
                if os.path.isfile(the_id) == False:            
                    if the_id.isdigit() == True:
                        grooveshark_id = the_id
                else:
                    music_id = the_id
 
                track_id = ratings_button.GetTrackId(artist, song, grooveshark_id, music_id)
                ratings_button.AddRating(self, track_id, 4)
                # only love the first one, don't want to hammer last.fm
                if need_love == True:
                    need_love = False
                    sk = self.parent.GenerateSessionKey2()
                    ratings_button.LoveTrack(artist, song, sk)
                val = self.parent.lc_playlist.GetNextSelected(val)
                     
        
    def SetFavesItem(self, current_count, artist, song, album, url, duration):
        
        #set value
        #index = self.lc_faves.InsertStringItem(current_count, artist)
        index = self.lc_faves.InsertImageStringItem(current_count, artist, 0)
        self.lc_faves.SetStringItem(current_count, 1, song)
        self.lc_faves.SetStringItem(current_count, 2, album)
        self.lc_faves.SetStringItem(current_count, 3, url)
        self.lc_faves.SetStringItem(current_count, 4, duration)
        
        self.ResizeFaves()
        
    #def SaveFaves(self, filename):
        # take current playlist and save to xml file
        #track_dict = []
        #print self.lc_playlist.GetItemCount()
        #for x in range(0, self.lc_faves.GetItemCount()):
            #print x
            #artist = self.lc_faves.GetItem(x, 0).GetText()
            #title = self.lc_faves.GetItem(x, 1).GetText()
            #album = self.lc_faves.GetItem(x, 2).GetText()
            #song_id = self.lc_faves.GetItem(x, 3).GetText()
            #duration = self.lc_faves.GetItem(x, 4).GetText()
            #track_dict.append({'creator': artist, 'title': title, 'album': album, 'location': song_id, 'duration': duration})
            
        #read_write_xml.xml_utils().save_tracks(filename, track_dict)
        
    def ReadFaves(self, query=None):
        self.lc_faves.DeleteAllItems()
        #populate favourites listctrl with songs that are rated 4 stars
        FILEDB = system_files.GetDirectories(None).DatabaseLocation()
        conn = sqlite3.connect(FILEDB)
        c = conn.cursor()
        if query == None:
            query = "SELECT artist, song, album, track_time, rating_type_id FROM m_rating INNER JOIN m_tracks ON m_rating.track_id = m_tracks.track_id WHERE rating_type_id = 4 ORDER BY artist, song"
        
        c.execute(query)
        h = c.fetchall()
        counter = 0
        for x in h:
            #print x
            try:
                #index = self.lc_faves.InsertStringItem(counter, x['creator'])
                index = self.lc_faves.InsertImageStringItem(counter, x[0], x[4])
                self.lc_faves.SetStringItem(counter, 1, x[1])
                album = x[2]
                if album == None:
                    album = ''
                self.lc_faves.SetStringItem(counter, 2, album)
                #song_id = x['location']
                song_id = ''
                #if song_id == None:
                    #song_id = ''
                self.lc_faves.SetStringItem(counter, 3, song_id)
                duration = self.parent.ConvertTimeFormated(x[3])
                if duration == None:
                    duration = ''
                self.lc_faves.SetStringItem(counter, 4, duration)
                counter = counter + 1
            except TypeError:
                pass
        c.close()
        self.ResizeFaves()
        
    def OnFavesDoubleClick(self, event):
        # get selected search relsult list item and add to playlist
        #val = event.GetIndex()
        val = self.lc_faves.GetFirstSelected()
        #items = self.lc_search.GetFirstSelected()
        #print val
        current_count = (self.parent.lc_playlist.GetItemCount())
        artist = self.lc_faves.GetItem(val, 0).GetText()
        song = self.lc_faves.GetItem(val, 1).GetText()
        album = self.lc_faves.GetItem(val, 2).GetText()
        url = self.lc_faves.GetItem(val, 3).GetText()
        duration = self.lc_faves.GetItem(val, 4).GetText()
        self.parent.SearchOrPlaylist(artist, song, album, url, duration)
        #self.SetPlaylistItem(current_count, artist, song, album, url, duration)
        
        # save playlist file
        self.parent.SavePlaylist(self.parent.main_playlist_location)
        
    def RemoveFavesItem(self, event=None):        
        # remove slected list item
        ##val = self.lc_faves.GetFirstSelected()
        # iterate over all selected items and delete
        ##for x in range(val, val + self.lc_faves.GetSelectedItemCount()):
            #print 'dete - ' + str(val)
            #self.lc_playlist.DeleteItem(val)
        ##    self.lc_faves.DeleteItem(self.lc_faves.GetFirstSelected())
        # save default playlist
        ##self.SaveFaves(self.faves_playlist_location)
        ##self.ResizeFaves()
        pass
        
    def ResizeFaves(self):
        # 
        self.lc_faves.SetColumnWidth(0, 160)
        self.lc_faves.SetColumnWidth(1, 210)
        self.lc_faves.SetColumnWidth(2, 145)
        self.lc_faves.SetColumnWidth(3, 0)#wx.LIST_AUTOSIZE)
        self.lc_faves.SetColumnWidth(4, 50)#wx.LIST_AUTOSIZE_USEHEADER)
        
    def OnAutoGenerateFavesPlayist(self, event):
        # copy the faves list to the playlist
        self.parent.CheckClear()
        self.parent.BackupList()
        insert_at = self.parent.lc_playlist.GetItemCount()
        for x in range(self.lc_faves.GetItemCount(), 0, -1):
            artist = self.lc_faves.GetItem(x-1, 0).GetText()
            song = self.lc_faves.GetItem(x-1, 1).GetText()
            album = self.lc_faves.GetItem(x-1, 2).GetText()
            song_id = self.lc_faves.GetItem(x-1, 3).GetText()
            duration = self.lc_faves.GetItem(x-1, 4).GetText()
            self.parent.SetPlaylistItem(insert_at, artist, song, album, song_id, duration)
        #save the playlist
        self.parent.SavePlaylist(self.parent.main_playlist_location)
        # switch tabs
        self.parent.nb_main.SetSelection(0) #NB_PLAYLIST)
        
    def OnFavesRightClick(self, event):
        val = self.lc_faves.GetFirstSelected()
        if val != -1:
            if (self.lc_faves.GetItem(val, 0).GetText() != '') & (self.lc_faves.GetItem(val, 1).GetText() != ''):    
                # make a menu
                ID_PLAYLIST = 13
                ID_CLEAR = 23
                menu = wx.Menu()
                menu.Append(ID_PLAYLIST, "Add to Playlist")                
                menu.Append(ID_CLEAR, "Clear Playlist")
                menu.AppendSeparator()
                wx.EVT_MENU(self.parent, ID_PLAYLIST, self.FavesAddPlaylist)
                wx.EVT_MENU(self.parent, ID_CLEAR, self.parent.OnClearPlaylistClick)
                #append the ratings menu
                re = self.SongRate
                ratings_button.MenuAppend(menu, self.parent, re)
                self.parent.PopupMenu(menu)
                menu.Destroy()
                
    def SongRate(self, event):
        #re-rate selected favourite list item
        event_id = event.GetId()
        val = self.lc_faves.GetFirstSelected()
        music_id = ''
        grooveshark_id = ''
        artist = self.lc_faves.GetItem(val, 0).GetText()
        song = self.lc_faves.GetItem(val, 1).GetText()
        track_id = ratings_button.GetTrackId(artist, song, grooveshark_id, music_id)
        ratings_button.AddRating(self, track_id, event_id)
        if event_id == 4:
            sk = self.parent.GenerateSessionKey2()
            LoveTrack(artist, song, sk)
  
    def FavesAddPlaylist(self, event):
        # add from favourite list to the playlist
        self.parent.BackupList()
        val = self.lc_faves.GetFirstSelected()
        total = self.lc_faves.GetSelectedItemCount()
        current_count = self.parent.lc_playlist.GetItemCount()
        #print val
        if (val >= 0):            
            artist =    self.lc_faves.GetItem(val, 0).GetText()
            song =      self.lc_faves.GetItem(val, 1).GetText()
            self.parent.SetPlaylistItem(current_count, artist, song, '', '')
            current_select = val
            if total > 1:
                for x in range(1, self.lc_faves.GetSelectedItemCount()):
                    current_select =    self.lc_faves.GetNextSelected(current_select)
                    artist =            self.lc_faves.GetItem(current_select, 0).GetText()
                    song =              self.lc_faves.GetItem(current_select, 1).GetText()                    
                    self.parent.SetPlaylistItem(current_count + x, artist, song, '', '')

        #save the playlist
        #self.SavePlaylist(self.main_playlist_location)
        # switch tabs
        #self.nb_main.SetSelection(NB_PLAYLIST)
        
    def OnFavesColClick(self, event):
        #excepts listcrtl column header click events and toggles sorting
        column = event.GetColumn()
        #self.faves_sorter = [0,0,0,0,0]
        toggle = self.faves_sorter[column]
                    
        query = "SELECT artist, song, album, track_time, rating_type_id FROM m_rating INNER JOIN m_tracks ON m_rating.track_id = m_tracks.track_id WHERE rating_type_id = 4 "
        order_by_arr = [["ORDER BY artist, song", "ORDER BY artist DESC, song", "ORDER BY rating_id", "ORDER BY rating_id DESC"],
            ["ORDER BY song, artist", "ORDER BY song DESC, artist", "ORDER BY rating_id", "ORDER BY rating_id DESC"],
            ["ORDER BY album, song", "ORDER BY album DESC, song", "ORDER BY rating_id", "ORDER BY rating_id DESC"],
            [],
            ["ORDER BY track_time, song", "ORDER BY track_time DESC, song", "ORDER BY rating_id", "ORDER BY rating_id DESC"]
            ]
        complete_query = query + order_by_arr[column][toggle]
        
        self.faves_sorter[column] = toggle + 1
        if toggle == 3:
            self.faves_sorter[column] = 0
        
        self.ReadFaves(complete_query)
        