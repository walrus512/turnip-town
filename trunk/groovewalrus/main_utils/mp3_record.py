"""
GrooveWalrus: Record mp3's | example taken from pymedia.org
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

import time, sys, os
import pymedia.audio.sound as sound
import pymedia.audio.acodec as acodec

from threading import Thread

SYSLOC = os.path.abspath(os.path.dirname(sys.argv[0]))
MP3_SAVE_LOCATION = SYSLOC + "\\mp3s\\"

class mp3_rec():
    # xml file junk for hippies
    def __init__(self):
        self.status = 'record'
        
    def stop(self):
        self.status = 'stop'
        #print self.status
        self.current.stop_it()
        
    def record(self, artist, song, record_dir, bitrate=128000): # , album):
        # just write the song as artist - song.mp3 for now 
        # must remove crazy characters from song/title to save as a file        
        aq = ''
        sq = ''
        #maybe something like str.encode('ascii','replace') might work
        for x in range(0, len(artist)):
            try:
                str(artist[x])
                aq = aq + str(artist[x])
            except UnicodeEncodeError:
                pass
                
        for y in range(0, len(song)):
            try:
                str(song[y])
                sq = sq + str(song[y])
            except UnicodeEncodeError:
                pass
                
        if (record_dir == None) | (record_dir == ''):
            record_dir = MP3_SAVE_LOCATION
                
        file_name = record_dir + replace_all(aq) + ' - ' + replace_all(sq) + '.mp3'
        #print file_name
        # THREAD
        self.current = RecordThread(file_name, bitrate)
        #THREAD
        self.current.start()
        

# ####################################
class RecordThread(Thread): 
    # grab rss feeds, thread style  
    def __init__(self, file_name, bitrate):
        Thread.__init__(self)
        self.status = "record"
        self.file_name = file_name
        self.bitrate = bitrate
        
    def stop_it(self):
        self.status = "stop"
        #print "stopped"
                
    def run(self):
        f= open( self.file_name, 'wb' )
        # Minimum set of parameters we need to create Encoder
        # getCodecID()
        cparams= { 'id': acodec.getCodecID( 'mp3' ),
             'bitrate': self.bitrate,
             'sample_rate': 44100,
             'channels': 2 } 
        ac= acodec.Encoder( cparams )
        #print sound.getODevices()
        #print sound.getIDevices()
        snd= sound.Input(44100, 2, sound.AFMT_S16_LE, 0)
        snd.start()
  
        # Loop until recorded position greater than the limit specified

        #while snd.getPosition()<= secs:
        while self.status == 'record':
            #print snd.getPosition()
            s= snd.getData()
            if s and len( s ):
                for fr in ac.encode( s ):
                # We definitely should use mux first, but for
                # simplicity reasons this way it'll work also
                    f.write( fr )
            else:
                time.sleep( .003 )
                #print 'boo'
  
        # Stop listening the incoming sound from the microphone or line in
        snd.stop()
       
#---------------------------------------------------------------------------
# ####################################
# ----------------------------------------------------------------------------------
# Record stereo sound from the line in or microphone and save it as mp3 file
# Specify length and output file name
# http://pymedia.org/

#if __name__ == "__main__":
#   if len( sys.argv )!= 3:
#       print 'Usage: mp3_recorder <seconds> <file_name>'
#   else:
#       mp3_recorder( int( sys.argv[ 1 ] ), sys.argv[ 2 ]  )

def replace_all(text):
    dic = {'\\':'', '/':'', ':':'', '?':'', '"':'', '<':'', '>':'', '|':''}
    #\\/:*?"<>|
    for i, j in dic.iteritems():
        text = text.replace(i, j)
    return text
