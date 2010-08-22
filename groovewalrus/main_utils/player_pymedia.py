# -*- coding: utf-8 -*-
"""
GrooveWalrus: pymedia player
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

import pymedia.muxer as muxer
import pymedia.audio.acodec as acodec
import pymedia.audio.sound as sound
import time
import os

from threading import Thread
from main_windows import options_window

EMULATE=0
BUFFER_SIZE = 320000

########################################################################
class Player(object): 
    def __init__(self, parent):
        self.local_play_status = True
        self.paused = False
        #self.snd = None
        self.play_thread = None
        self.parent = parent
                
    def Play(self, file_name):
        #print file_name
        #source = pyglet.media.load(file_name)
        #self.mediaPlayer.queue(source)
        self.play_thread = PlayThread(file_name, self.parent)
        #THREAD
        self.play_thread.start()
        
        
    def Stop(self):
        """ Stop playing the current file """
        if self.play_thread != None:
            self.play_thread.stop()
        
    def SetVolume(self, volume):
        pass        
            
    def TogglePause(self, status):
        if self.play_thread != None:
            self.play_thread.toggle_pause()
            
class PlayThread(Thread):
    """ makes a thread for pymedia playback """
    def __init__(self, file_name, parent):
        Thread.__init__(self)
        self.paused = False
        self.file_name = file_name
        self.local_play_status = True
        self.snd = None
        self.parent = parent
        
    def run(self):
        """ plays a god-damn song """
        
        #local mp3 playback 
        print 'local: ' + self.file_name
        self.parent.current_song.status = 'loading'
        while os.path.isfile(self.file_name) != True:
            time.sleep(1)
            
        get_buffer = options_window.GetSetting('buffer-size-bytes', self.parent.FILEDB)
        if get_buffer != False:
            buffer_sz = int(get_buffer)
        else:
            buffer_sz = BUFFER_SIZE
        while os.path.getsize(self.file_name) < buffer_sz:
            time.sleep(2)
            #print os.path.getsize(file_name)
        self.parent.time_count = -1
        self.parent.current_song.status = 'playing'
            
        
        card=0
        rate=1
        tt=-1    
        #dm= muxer.Demuxer( str.split( name, '.' )[ -1 ].lower() )
        dm= muxer.Demuxer( 'mp3' )
        snds= sound.getODevices()
        if card not in range( len( snds ) ):
            raise 'Cannot play sound to non existent device %d out of %d' % ( card+ 1, len( snds ) )
        f= open( self.file_name, 'rb' )
        self.snd= resampler= dec= None
        s= f.read( 32000 )
        t= 0
        while (len( s )):
            #print self.local_play_status
            frames= dm.parse( s )
            if frames:
                for fr in frames:
                # Assume for now only audio streams
    
                    if dec== None:
                        #print dm.getHeaderInfo(), dm.streams
                        dec= acodec.Decoder( dm.streams[ fr[ 0 ] ] )
            
                    r= dec.decode( fr[ 1 ] )
                    if r and r.data:
                        if self.snd== None:
                            #print 'Opening sound with %d channels -> %s' % ( r.channels, snds[ card ][ 'name' ] )
                            self.snd= sound.Output( int( r.sample_rate* rate ), r.channels, sound.AFMT_S16_LE, card )
                            #print r.channels
                            if rate< 1 or rate> 1:
                                resampler= sound.Resampler( (r.sample_rate,r.channels), (int(r.sample_rate/rate),r.channels) )
                                print 'Sound resampling %d->%d' % ( r.sample_rate, r.sample_rate/rate )
              
                        data= r.data
                        if resampler:
                            data= resampler.resample( data )
                        if EMULATE:
                            # Calc delay we should wait to emulate snd.play()
    
                            d= len( data )/ float( r.sample_rate* r.channels* 2 )
                            time.sleep( d )
                            if int( t+d )!= int( t ):
                                print 'playing: %d sec\r' % ( t+d ),
                            t+= d
                        else:
                            self.snd.play( data )
                        #print snd.getPosition()
            if tt> 0:
                if self.snd and self.snd.getPosition()< tt:
                    break

            s= f.read( 512 )
            if self.local_play_status == False:               
                break
                    
        while self.snd.isPlaying():
            time.sleep( 0.05 )
          
    def stop(self):
        self.local_play_status = False
        if os.name != 'nt':
            time.sleep(4)
            
    def toggle_pause(self):
        if self.snd:
            if self.paused == False:
                self.pause()
            else:
                self.unpause()
                
    def pause(self):
        """ Pause playing the current file """
        if self.snd.isPlaying():
            self.paused= True
            if self.snd:
                self.snd.pause()
                
    def unpause(self):
        """ Resume playing the current file """
        if self.snd.isPlaying():
            if self.snd:
                self.snd.unpause()
        self.paused= False