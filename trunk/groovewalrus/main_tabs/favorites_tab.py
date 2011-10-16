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
#from main_utils import local_songs

#columns
C_RATING = 0
C_ARTIST = 1
C_SONG = 2
C_ALBUM = 3
C_ID = 4
C_TIME = 5

CP_RATING = 0
CP_ARTIST = 1
CP_SONG = 2
CP_ALBUM = 3
CP_ID = 4
CP_TIME = 5

R_GREAT = 4
R_GOOD = 3
R_AVERAGE = 2
R_POOR = 1

class FavoritesTab(wx.ScrolledWindow):
    def __init__(self, parent):
        self.parent = parent

        # controls
        self.cb_faves_great = xrc.XRCCTRL(self.parent, 'm_cb_faves_great')
        self.cb_faves_good = xrc.XRCCTRL(self.parent, 'm_cb_faves_good')
        self.cb_faves_average = xrc.XRCCTRL(self.parent, 'm_cb_faves_average')
        self.cb_faves_poor = xrc.XRCCTRL(self.parent, 'm_cb_faves_poor')
        self.st_faves_rating = xrc.XRCCTRL(self.parent, 'm_st_faves_rating')
        
        # faves list control
        self.lc_faves = xrc.XRCCTRL(self.parent, 'm_lc_faves')
        self.lc_faves.InsertColumn(C_RATING," ")
        self.lc_faves.InsertColumn(C_ARTIST,"Artist")
        self.lc_faves.InsertColumn(C_SONG,"Song")
        self.lc_faves.InsertColumn(C_ALBUM,"Album")
        self.lc_faves.InsertColumn(C_ID,"Id")
        self.lc_faves.InsertColumn(C_TIME,"Time")        
        self.parent.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.FavesAddPlaylist, self.lc_faves)
        # wxMSW
        self.parent.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnFavesRightClick, self.lc_faves)
        # wxGTK
        self.lc_faves.Bind(wx.EVT_RIGHT_UP, self.OnFavesRightClick)
        #self.lc_faves.Bind(wx.EVT_KEY_UP, self.OnDeleteClick)
        self.lc_faves.Bind(wx.EVT_LIST_COL_CLICK, self.OnFavesColClick)
                
        self.faves_sorter = [0,1,0,0,0,0]
        
        self.lc_faves.Bind(wx.EVT_KEY_DOWN, self.OnKeyPress)
        self.lc_faves.Bind(wx.EVT_CHAR, self.parent.OnChar)
        
        self.lc_faves.AssignImageList(self.parent.RateImageList(), wx.IMAGE_LIST_SMALL)        
        self.lc_faves.SetColumnImage(1, 5)
        
        #bindings        
        self.parent.Bind(wx.EVT_BUTTON, self.OnFavesClick, id=xrc.XRCID('m_bb_faves'))
        self.parent.Bind(wx.EVT_BUTTON, self.FavesAddPlaylist, id=xrc.XRCID('m_bb_faves_playlist'))
        self.st_faves_rating.Bind(wx.EVT_LEFT_UP, self.OnFavesRatingLabelClick)
        
        self.parent.Bind(wx.EVT_BUTTON, self.OnAutoGenerateFavesPlayist, id=xrc.XRCID('m_bb_faves_plize'))
        
        self.parent.Bind(wx.EVT_CHECKBOX, self.FilterFaves, id=xrc.XRCID('m_cb_faves_great'))
        self.parent.Bind(wx.EVT_CHECKBOX, self.FilterFaves, id=xrc.XRCID('m_cb_faves_good'))
        self.parent.Bind(wx.EVT_CHECKBOX, self.FilterFaves, id=xrc.XRCID('m_cb_faves_average'))
        self.parent.Bind(wx.EVT_CHECKBOX, self.FilterFaves, id=xrc.XRCID('m_cb_faves_poor'))
        
# --------------------------------------------------------- 
# faves  -------------------------------------------------- 
  
    def FilterFaves(self, event):
        self.OnFavesColClick()
        
    def OnFavesRatingLabelClick(self, event):
        #toggle between selecting all, and none
        if self.cb_faves_great.GetValue() == True:
            #select none
            self.cb_faves_great.SetValue(False)
            self.cb_faves_good.SetValue(False)
            self.cb_faves_average.SetValue(False)
            self.cb_faves_poor.SetValue(False)
            self.FilterFaves(None)
        else:
            self.cb_faves_great.SetValue(True)
            self.cb_faves_good.SetValue(True)
            self.cb_faves_average.SetValue(True)
            self.cb_faves_poor.SetValue(True)
            self.FilterFaves(None)
        
        
    def OnKeyPress(self, event):
        #jump to next artist with that starting letter
        keycode = event.GetKeyCode()
        if (keycode > 64) & (keycode < 123):
            list_item = 0
            first_letter = self.lc_faves.GetItem(list_item, C_ARTIST).GetText()[0].upper()
            while list_item < self.lc_faves.GetItemCount():
                first_letter = self.lc_faves.GetItem(list_item, C_ARTIST).GetText()[0].upper()
                if first_letter == chr(keycode):
                    break
                list_item = list_item + 1
            self.lc_faves.Focus(list_item)
        event.Skip() #handle event Char too
            
    def OnFavesClick(self, event):
        # get current song and add to favourites list
        # this is not the same as clicking from the playlist
        
        music_id = self.parent.current_song.track_id
        grooveshark_id = self.parent.current_song.groove_id
        artist = self.parent.current_song.artist
        song = self.parent.current_song.song
        
        track_id = ratings_button.GetTrackId(artist, song, grooveshark_id, music_id)
        ratings_button.AddRating(self.parent, track_id, R_GREAT)
        
        #upadte playlist item to display the fave icon
        list_num = self.parent.current_song.playlist_position
        pl_artist = self.parent.lc_playlist.GetItem(list_num, CP_ARTIST).GetText()
        pl_song = self.parent.lc_playlist.GetItem(list_num, CP_SONG).GetText()
        #check that the playlist item we're updateing matches
        if (pl_artist == artist) & (pl_song == song):
            self.parent.GetSongRating(track_id, list_num) 
        
        network = self.parent.GetNetwork()
        ratings_button.LoveTrack(artist, song, network)        
        
    def OnPlaylistFavesClick(self, event):
        # add a favorite (or many faves) from the right-click menu on the playlist
        val = self.parent.lc_playlist.GetFirstSelected()
        # check if something is selected
        need_love = True
        if val >= 0:
        #    current_count = (self.lc_faves.GetItemCount())
            for x in range(0, self.parent.lc_playlist.GetSelectedItemCount()):
                artist = self.parent.lc_playlist.GetItem(val, CP_ARTIST).GetText()
                song = self.parent.lc_playlist.GetItem(val, CP_SONG).GetText()
                grooveshark_id = ''
                music_id = ''
                
                the_id = self.parent.lc_playlist.GetItem(val, CP_ID).GetText()
                if os.path.isfile(the_id) == False:            
                    if the_id.isdigit() == True:
                        grooveshark_id = the_id
                else:
                    music_id = the_id
 
                track_id = ratings_button.GetTrackId(artist, song, grooveshark_id, music_id)
                ratings_button.AddRating(self.parent, track_id, R_GREAT)
                
                #upadte playlist item to display the fave icon
                self.parent.GetSongRating(track_id, val)                
                
                # only love the first one, don't want to hammer last.fm
                if need_love == True:
                    need_love = False
                    network = self.parent.GetNetwork()
                    ratings_button.LoveTrack(artist, song, network)
                val = self.parent.lc_playlist.GetNextSelected(val)
                

        
    def SetFavesItem(self, current_count, artist, song, album, url, duration):
        
        #set value
        #index = self.lc_faves.InsertStringItem(current_count, artist)
        index = self.lc_faves.InsertImageStringItem(current_count, '', C_RATING)
        self.lc_faves.SetStringItem(current_count, C_ARTIST, artist)
        self.lc_faves.SetStringItem(current_count, C_SONG, song)
        self.lc_faves.SetStringItem(current_count, C_ALBUM, album)
        self.lc_faves.SetStringItem(current_count, C_ID, url)
        self.lc_faves.SetStringItem(current_count, C_TIME, duration)
        
        #self.ResizeFaves()
              
    def SetRatingFilters(self):
        #create the where clause to filter based on ratings
        rating_string = ' WHERE '
        #get the checkbox fileters
        if self.cb_faves_great.GetValue() == True:
            rating_string = rating_string + ' rating_type_id = 4 '
        if self.cb_faves_good.GetValue() == True:
            connector = ''
            if len(rating_string) > 7:
                connector = ' OR '
            rating_string = rating_string + connector + ' rating_type_id = 3 '
        if self.cb_faves_average.GetValue() == True:
            connector = ''
            if len(rating_string) > 7:
                connector = ' OR '
            rating_string = rating_string + connector +  ' rating_type_id = 2 '
        if self.cb_faves_poor.GetValue() == True:
            connector = ''
            if len(rating_string) > 7:
                connector = ' OR '
            rating_string = rating_string + connector +  ' rating_type_id = 1 '
        if len(rating_string) == 7:
            rating_string = ' WHERE  rating_type_id = 4 '    
        return rating_string
        
    def ReadFaves(self, query=None):
        self.lc_faves.DeleteAllItems()
        #populate favourites listctrl with songs that are rated 4 stars
        FILEDB = system_files.GetDirectories(None).DatabaseLocation()
        conn = sqlite3.connect(FILEDB)
        c = conn.cursor()
            
        rating_string = self.SetRatingFilters()
        
        if query == None:
            query = "SELECT artist, song, album, track_time, rating_type_id FROM m_rating INNER JOIN m_tracks ON m_rating.track_id = m_tracks.track_id " + rating_string + " ORDER BY artist, song"
        
        c.execute(query)
        h = c.fetchall()
        counter = 0
        for x in h:
            #print x
            try:
                #index = self.lc_faves.InsertStringItem(counter, x['creator'])
                index = self.lc_faves.InsertImageStringItem(counter, '', x[4])
                self.lc_faves.SetStringItem(counter, C_ARTIST, x[0])
                self.lc_faves.SetStringItem(counter, C_SONG, x[1])
                album = x[2]
                if album == None:
                    album = ''
                self.lc_faves.SetStringItem(counter, C_ALBUM, album)
                #song_id = x['location']
                song_id = ''
                #if song_id == None:
                    #song_id = ''
                self.lc_faves.SetStringItem(counter, C_ID, song_id)
                duration = self.parent.ConvertTimeFormated(x[3])
                if duration == None:
                    duration = ''
                self.lc_faves.SetStringItem(counter, C_TIME, duration)
                counter = counter + 1
            except TypeError:
                pass
        c.close()
        #self.ResizeFaves()
                
    def ResizeFaves(self):
        # 
        self.lc_faves.SetColumnWidth(C_RATING, 25)
        self.lc_faves.SetColumnWidth(C_ARTIST, 160)
        self.lc_faves.SetColumnWidth(C_SONG, 230)
        self.lc_faves.SetColumnWidth(C_ALBUM, 140)
        self.lc_faves.SetColumnWidth(C_ID, 0)#wx.LIST_AUTOSIZE)
        self.lc_faves.SetColumnWidth(C_TIME, 50)#wx.LIST_AUTOSIZE_USEHEADER)
        
    def DyRes(self):
        """ Resizes the listcontrol dynamically """
        flex_max = self.lc_faves.GetSize()[0] - (25 + 50)
        #print self.lc_playlist.GetSize()[0]
        if flex_max > 1000:
            flex_max = 1000
        self.lc_faves.SetColumnWidth(C_RATING, 25)
        self.lc_faves.SetColumnWidth(C_ARTIST, flex_max*.28)
        self.lc_faves.SetColumnWidth(C_SONG, flex_max*.38)
        self.lc_faves.SetColumnWidth(C_ALBUM, flex_max*.28)
        self.lc_faves.SetColumnWidth(C_ID, 0)
        self.lc_faves.SetColumnWidth(C_TIME, 50)#wx.LIST_AUTOSIZE_USEHEADER)

             
    def OnFavesRightClick(self, event):
        val = self.lc_faves.GetFirstSelected()
        if val != -1:
            if (self.lc_faves.GetItem(val, C_ARTIST).GetText() != '') & (self.lc_faves.GetItem(val, C_SONG).GetText() != ''):    
                # make a menu
                ID_PLAYLIST = 13
                ID_CLEAR = 23
                ID_RATE_CLEAR = 33
                menu = wx.Menu()
                menu.Append(ID_PLAYLIST, "Add to Playlist")                
                menu.Append(ID_CLEAR, "Clear Playlist")
                menu.AppendSeparator()
                wx.EVT_MENU(self.parent, ID_PLAYLIST, self.FavesAddPlaylist)
                wx.EVT_MENU(self.parent, ID_CLEAR, self.parent.OnClearPlaylistClick)
                #append the ratings menu
                re = self.SongRate
                ratings_button.MenuAppend(menu, self.parent, re)
                menu.AppendSeparator()
                menu.Append(ID_RATE_CLEAR, "Clear Rating")
                wx.EVT_MENU(self.parent, ID_RATE_CLEAR, self.OnClearRatingClick)
                self.parent.PopupMenu(menu)
                menu.Destroy()
                
    def SongRate(self, event):
        #re-rate selected favourite list item
        event_id = event.GetId()
        val = self.lc_faves.GetFirstSelected()
        music_id = ''
        grooveshark_id = ''
        artist = self.lc_faves.GetItem(val, C_ARTIST).GetText()
        song = self.lc_faves.GetItem(val, C_SONG).GetText()
        track_id = ratings_button.GetTrackId(artist, song, grooveshark_id, music_id)
        ratings_button.AddRating(self.parent, track_id, event_id)
        if event_id == 4:
            network = self.parent.GetNetwork()
            ratings_button.LoveTrack(artist, song, network)
            
    def OnClearRatingClick(self, event):
        val = self.lc_faves.GetFirstSelected()
        music_id = ''
        grooveshark_id = ''
        artist = self.lc_faves.GetItem(val, C_ARTIST).GetText()
        song = self.lc_faves.GetItem(val, C_SONG).GetText()
        track_id = ratings_button.GetTrackId(artist, song, grooveshark_id, music_id)
        ratings_button.AddRating(self, track_id, 0)
        
    def OnFavesColClick(self, event=None):
        #excepts listcrtl column header click events and toggles sorting
        try:
            column = event.GetColumn()
            no_inc = False
        except AttributeError:
            column = 0
            #don't increment the sort, when changing the filter
            no_inc = True        
        #self.faves_sorter = [0,0,0,0,0]
        toggle = self.faves_sorter[column]        
        rating_string = self.SetRatingFilters()
        
        query = "SELECT artist, song, album, track_time, rating_type_id FROM m_rating INNER JOIN m_tracks ON m_rating.track_id = m_tracks.track_id " + rating_string #WHERE rating_type_id = 4 "
        order_by_arr = [
            ["ORDER BY rating_type_id DESC, artist, song", "ORDER BY rating_type_id, artist , song", "ORDER BY rating_id", "ORDER BY rating_id DESC"],
            ["ORDER BY artist, song", "ORDER BY artist DESC, song", "ORDER BY rating_id", "ORDER BY rating_id DESC"],
            ["ORDER BY song, artist", "ORDER BY song DESC, artist", "ORDER BY rating_id", "ORDER BY rating_id DESC"],
            ["ORDER BY album, song", "ORDER BY album DESC, song", "ORDER BY rating_id", "ORDER BY rating_id DESC"],
            [],
            ["ORDER BY track_time, song", "ORDER BY track_time DESC, song", "ORDER BY rating_id", "ORDER BY rating_id DESC"]
            ]
        complete_query = query + order_by_arr[column][toggle]
        
        #column header graphic
        for x in range(0, 6):
            self.lc_faves.SetColumnImage(x, 9)
        self.lc_faves.SetColumnImage(column, toggle+5)
        
        
        
        if no_inc == False:
            self.faves_sorter[column] = toggle + 1
            if toggle == 3:
                self.faves_sorter[column] = 0
        
        self.ReadFaves(complete_query)
        
    # playlist adding ---------------
                
    def OnAutoGenerateFavesPlayist(self, event):
        """ add all the list items to the playlist """
        self.parent.AddAll(self.lc_faves, num_cols=5)
        
    def FavesAddPlaylist(self, event):
        """ add the selected list items to the playlist """
        self.parent.AddSelected(self.lc_faves, num_cols=5)
        