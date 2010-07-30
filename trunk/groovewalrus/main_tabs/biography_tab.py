"""
GrooveWalrus: Biography Tab
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
import time
from threading import Thread
from main_utils import audioscrobbler_lite
from main_utils import file_cache

class BiographyTab(wx.ScrolledWindow):
    def __init__(self, parent):
        self.parent = parent

        # controls
        self.bm_bio_pic = xrc.XRCCTRL(self.parent, 'm_bm_bio_pic')
        self.hm_bio_text = xrc.XRCCTRL(self.parent, 'm_hm_bio_text')        
        
# ---------------------------------------------------------
# biography  ----------------------------------------------
    def GetArtistBio(self, artist):
        # get song's album from musicbrainz
        # THREAD
        current = BioThread(self.parent, artist)
        #THREAD
        current.start()
        
    def SetBioImage(self, file_name):
        """ sets the picture for the biography """
        # get albumcover for artist/song from last.fm
        bio_bmp = wx.Bitmap(self.parent.image_save_location + file_name, wx.BITMAP_TYPE_ANY) #wx.BITMAP_TYPE_JPEG)
        #self.bm_bio_pic.SetSize(bio_bmp.GetSize())
        #self.bm_bio_pic.SetBitmap(bio_bmp)
        bb = bio_bmp.GetSize()        
        hr = float(bb[0]) / 250
        hs = float(bb[1]) / hr
        # rescale it so it's x= 250 y =? to keep aspect
        hoo = wx.Bitmap.ConvertToImage(bio_bmp)
        hoo.Rescale(250, hs) #, wx.IMAGE_QUALITY_HIGH)
        ioo = wx.BitmapFromImage(hoo)
        self.bm_bio_pic.SetBitmap(ioo)

    def SetBioText(self, bio_text, artist):
        """ sets the biography text """
        # get albumcover for artist/song from last.fm
        bio_text_str = self.StripTags(bio_text)
        page_contents = '<p><FONT SIZE=3><b>' + unicode(artist) + '</b></FONT><br><br><FONT SIZE=-1>' + unicode(bio_text_str) + '</FONT></p>'
        self.hm_bio_text.SetPage(page_contents)
        
    def StripTags(self, text):
        """ strips out html tags """
        finished = 0
        if (text != None):
            if (len(text) > 0):
                while not finished:
                    finished = 1
                    # check if there is an open tag left
                    start = text.find("<")
                    if start >= 0:
                        # if there is, check if the tag gets closed
                        stop = text[start:].find(">")
                        if stop >= 0:
                            # if it does, strip it, and continue loop
                            text = text[:start] + text[start+stop+1:]
                            finished = 0
        return text
        
#---------------------------------------------------------------------------
# ####################################
class BioThread(Thread): 
    # grab rss feeds, thread style  
    def __init__(self, parent, artist):
        Thread.__init__(self)        
        self.parent = parent
        self.artist = artist
                 
    def run(self):
        bio_url =''
        if len(self.artist) > 0:
            # try album art if nothing is listed for the song
            bio_url = audioscrobbler_lite.Scrobb().get_artist_bio(self.artist)
            #print bio_url[0]
        if len(str(bio_url[0])) > 8:
            file_name = bio_url[0].rsplit('/', 1)[1]
            ext = '.' + file_name.rsplit('.', 1)[1]                
            (local_file_name, is_file) = file_cache.CreateCachedImage(self.parent.image_save_location, self.artist, ext)                
            if is_file == False:
                self.parent.SaveSongArt(bio_url[0], local_file_name)
            self.parent.tab_biography.SetBioImage(local_file_name)
            #if there's no album art set the bio image as the album cover
            time.sleep(3)
            if self.parent.palbum_art_file =='':                    
                self.parent.SetImage(local_file_name, self.parent.image_save_location, resize=True)
        self.parent.tab_biography.SetBioText(bio_url[1], self.artist)