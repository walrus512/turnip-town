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
from wx.lib.embeddedimage import PyEmbeddedImage
import time
import os
from threading import Thread
from main_utils import audioscrobbler_lite
from main_utils import file_cache
from main_thirdp import google_translation
from main_windows import options_window

EVT_NEW_IMAGE = wx.PyEventBinder(wx.NewEventType(), 0)
EVT_NEW_IMAGE2 = wx.PyEventBinder(wx.NewEventType(), 0)

class ImageEvent(wx.PyCommandEvent):
    def __init__(self, eventType=EVT_NEW_IMAGE.evtType[0], id=0):
        wx.PyCommandEvent.__init__(self, eventType, id)
        self.data = None
        
class ImageEvent2(wx.PyCommandEvent):
    def __init__(self, eventType=EVT_NEW_IMAGE2.evtType[0], id=0):
        wx.PyCommandEvent.__init__(self, eventType, id)
        self.data = None

class BiographyTab(wx.ScrolledWindow):
    def __init__(self, parent):
        self.parent = parent 
        #bio_diag =  wx.Dialog(parent, -1, "Biotext", style=wx.FRAME_SHAPED)
        #bio_diag.SetSize((400,200))
        #bio_diag.Show(True)
        #bio_panel = wx.Panel(bio_diag, -1)
        #self.hm_bio_text = wx.StaticText(self, -1)
        self.pa_bio_pic = xrc.XRCCTRL(self.parent, 'm_pa_bio_pic')
        self.st_bio_artist = xrc.XRCCTRL(self.parent, 'm_st_bio_artist')
        self.ht_bio_text = xrc.XRCCTRL(self.parent, 'm_ht_bio_text')
        
        self.background_file = ''
        
        self.pa_bio_pic.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.pa_bio_pic.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.pa_bio_pic.Bind(wx.EVT_LEFT_UP, self.OnBackgroundClick)
        self.ht_bio_text.Bind(wx.EVT_LEFT_UP, self.OnBackgroundClick)
        
        self.parent.Bind(EVT_NEW_IMAGE, self.UpdateBio)
        self.parent.Bind(EVT_NEW_IMAGE2, self.UpdateImage)
        
# ---------------------------------------------------------
# biography  ----------------------------------------------
    def GetArtistBio(self, artist):
        # get song's album from musicbrainz
        #set text label
        self.st_bio_artist.SetLabel(unicode(artist))
        self.background_file = ''
        (local_file_name, is_file) = file_cache.CreateCachedImage(self.parent.image_save_location, artist, '.jpg')
        if is_file == True:
            self.background_file = self.parent.image_save_location + local_file_name
            self.pa_bio_pic.Refresh()
        # THREAD
        current = BioThread(self.parent, artist, self, local_file_name)
        #THREAD
        current.start()
        
    def UpdateBio(self, event):
        #(bio_url[1], self.artist)
        if event.data != None:
            self.SetBioText(event.data[0], event.data[1])
        else:
            self.pa_bio_pic.Refresh()
        
    def UpdateImage(self, event):
        #(bio_url[1], self.artist)
        self.parent.SetImage(event.data, self.parent.image_save_location, resize=True)
            
    def SetBioText(self, bio_text, artist):
        """ sets the biography text """

        # get albumcover for artist/song from last.fm
        bio_text_str = StripTags(bio_text)
        tranny = 'en'
        lang_set = options_window.GetSetting('language-selected', self.parent.FILEDB)
        if (lang_set != False): #& (lang != None):
            tranny = wx.Locale(int(lang_set)).GetCanonicalName()[0:2]
        if tranny != 'en':
            try:
                bio_text_str = google_translation.translate(bio_text_str, to=tranny)
            except Exception, expt:
                print "biography_tab:" + str(Exception) + str(expt)    
        page_contents = '<FONT SIZE=-1>' + unicode(bio_text_str) + '</FONT>'
        self.ht_bio_text.SetPage(page_contents)    
    
    def OnBackgroundClick(self, event):
        if self.ht_bio_text.IsShown():
            self.ht_bio_text.Show(False)
        else:
            self.ht_bio_text.Show(True)
        self.pa_bio_pic.Refresh()    
        event.Skip()
        
    def OnEraseBackground(self, event):
        """ Add a picture to the background """
        pt = PyEmbeddedImage(
            "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAAA3NCSVQICAjb4U/gAAAAQElE"
            "QVRIiWM8cOAAAy0BE01NHxYWsECoAwcciNTg4HCAJAuGfhCNWjDwFjCOFhWjFoxaMGrBqAWj"
            "FoxaMDIsAABPtQfBbeinLQAAAABJRU5ErkJggg==")            
        
        # yanked from ColourDB.py
        dc = event.GetDC()
    
        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)
        dc.Clear()
        if (os.path.isfile(self.background_file)):        
            bmp = wx.Bitmap(self.background_file)
        else:
            bmp = pt.GetBitmap()
        #self.bm_bio_pic.SetSize(bio_bmp.GetSize())
        #self.bm_bio_pic.SetBitmap(bio_bmp)
        bb = bmp.GetSize()
        hr = float(bb[0]) / self.pa_bio_pic.GetClientSize()[0]
        hs = float(bb[1]) / hr
        # rescale it so it's x= 250 y =? to keep aspect
        hoo = wx.Bitmap.ConvertToImage(bmp)
        hoo.Rescale(self.pa_bio_pic.GetClientSize()[0], hs) #, wx.IMAGE_QUALITY_HIGH)                
        vshift = (bb[1] * -0.20)
        if bb[1] > bb[0]:
            vshift = ((bb[1] - bb[0]) * -1) + (bb[1] * 0.20)
        
        ioo = wx.BitmapFromImage(hoo)
        ###self.bm_bio_pic.SetBitmap(ioo)
        dc.DrawBitmap(ioo, 0, vshift)
        ##w, h = self.pa_bio_pic.GetClientSize()
        ##dc.SetBrush(wx.BrushFromBitmap(wx.Bitmap(self.background_file)))
        ##dc.DrawRectangle(0, 0, w, h)
        event.Skip()
             
#---------------------------------------------------------------------------
# ####################################
class BioThread(Thread): 
    # grab rss feeds, thread style  
    def __init__(self, parent, artist, tab, local_file_name):
        Thread.__init__(self)        
        self.parent = parent
        self.artist = artist
        self.tab = tab
        self.local_file_name = local_file_name
        #self.bio_text = bio_text
                
        # controls
        self.ht_bio_text = xrc.XRCCTRL(self.parent, 'm_ht_bio_text')
        
        
        #self.x_dim = self.bm_bio_pic.GetSize()[0]
        #self.y_dim = self.bm_bio_pic.GetSize()[1]
                 
    def run(self):
        local_file_name = self.local_file_name
        self.tab.pa_bio_pic.Refresh()
        if len(self.artist) > 0:
            # try album art if nothing is listed for the song
            bio_url = audioscrobbler_lite.Scrobb().get_artist_bio(self.artist)
            #print bio_url[0]
            if len(bio_url) > 1:
                #self.SetBioText(bio_url[1], self.artist)
                event = ImageEvent()
                event.data = (bio_url[1], self.artist)
                wx.PostEvent(self.parent, event)                
                
            if (len(str(bio_url[0])) > 8) & (self.tab.background_file ==''):
                file_name = bio_url[0].rsplit('/', 1)[1]
                ext = '.' + file_name.rsplit('.', 1)[1]                
                (local_file_name, is_file) = file_cache.CreateCachedImage(self.parent.image_save_location, self.artist, ext)                
                if is_file == False:
                    self.parent.SaveSongArt(bio_url[0], local_file_name)
                self.tab.background_file = self.parent.image_save_location + local_file_name
                #self.tab.pa_bio_pic.Refresh()
                event = ImageEvent()
                event.data = None
                wx.PostEvent(self.parent, event)
                #if there's no album art set the bio image as the album cover
            time.sleep(3)
            if self.parent.palbum_art_file =='':
                event = ImageEvent2()
                event.data = local_file_name
                wx.PostEvent(self.parent, event)
                #self.parent.SetImage(local_file_name, self.parent.image_save_location, resize=True)    

def StripTags(text):
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