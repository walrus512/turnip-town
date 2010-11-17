#http://www.bearhome.net/mpy3/
#mpcVolume.py

import ossaudiodev

class OSSVolumeControl(object):    
    def __init__(self):        
        #self.type = OSS
        #if self.options.has_key('device'):
        #    self.mixer = ossaudiodev.openmixer(self.options['device'])
        #else:
        self.mixer = ossaudiodev.openmixer()

        #if self.options.has_key('control'):
        #    self.volume = eval("ossaudiodev.%s" % (self.options['control']))
        if self.mixer.controls() & (1 << ossaudiodev.SOUND_MIXER_PCM):
            self.volume = ossaudiodev.SOUND_MIXER_PCM
        elif self.mixer.controls() & (1 << ossaudiodev.SOUND_MIXER_VOLUME):
            self.volume = ossaudiodev.SOUND_MIXER_VOLUME
        else:
            raise Exception, "No volume control found!"

    def get(self):
        return self.mixer.get(self.volume)

    def set(self, left, right):
        if (left | right != 0):            
            l, r = self.mixer.set(self.volume, (left, right))
        #if self.muted and l > 0 or r > 0:
        #    self.muted = False
        #return l, r

    #def unmute(self):
     #   if self.muted:
     #       self.set(self.mute_store[0], self.mute_store[1])
     #       self.muted = False

   # def mute(self):
     #   if not self.muted:
     #       self.mute_store = self.get()
     #       self.muted = True
      #      self.set(0, 0)

def SetMasterVolume(volume):
    try:
        v = OSSVolumeControl().set(volume, volume)
    except Exception, expt:
        #print u"soundmixer_linux: " + str(Exception) + str(expt)
        pass

def GetMasterVolume():
    try:
        v = OSSVolumeControl().get()
        return v[0]
    except Exception, expt:
        #print u"soundmixer_linux: " + str(Exception) + str(expt)
        return None
        #return 50