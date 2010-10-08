"""
GrooveWalrus: setting/using system files and folders
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

import sys, os
import shutil
import wx


#SYSLOC = os.path.abspath(os.path.dirname(sys.argv[0]))
#MP3_SAVE_LOCATION = DATA_DIR + "/mp3s/"
#os.path.join()
#os.sep
# mp3s
# playlists

class GetDirectories(object):
    def __init__(self, parent):
        self.sp = wx.StandardPaths.Get()        
        wx.GetApp().SetAppName("GrooveWalrus")
        self.parent = parent        
        
    def IsPortable(self):
        # check for portable mode
        for x in range(0, len(sys.argv)):
            if sys.argv[x] == '-p=true':
                #print 'portable'
                return True
        return False
        
    def GetPortablePath(self):
        # check for portable mode
        for x in range(0, len(sys.argv)):
              if sys.argv[x][0:4] == '-pp=':
                #print sys.argv[x]
                portable_path = sys.argv[x][4:]
                return portable_path
        return False
        
    def IsPortablePathCache(self):
        # check for portable mode
        for x in range(0, len(sys.argv)):
            if sys.argv[x] == '-ppc=false':
                #print 'portable'
                return False
        return True
        
    def DataDirectory(self):
  
        if self.IsPortable():
            if self.GetPortablePath() == False:
                u_dir = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), 'portable')
            else:
                u_dir = self.GetPortablePath()
            print u_dir
            #if os.path.isfile(os.path.join(u_dir, "layout.xml")) == False:
                #u_dir = os.path.join(os.path.abspath(os.getcwd()), 'portable')
        else:        
            u_dir = string_wrap(self.sp.GetUserDataDir())
            
        if os.path.isdir(u_dir) == False:
            try:
                os.mkdir(u_dir)
            except:
                dlg = wx.MessageDialog(self.parent, "Can't create directory\r\n %s" % (u_dir), 'Alert', wx.OK | wx.ICON_WARNING)
                if (dlg.ShowModal() == wx.ID_OK):
                    dlg.Destroy()
        
        return u_dir
        
    def TempDirectory(self):

        if self.IsPortable():
            if self.GetPortablePath() == False:
                #use regular portable path
                p_name = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), 'portable')
            else:
                #use custom portable path
                if self.IsPortablePathCache():
                    #check if we want to use the custom portable path to cache files
                    p_name = self.GetPortablePath()
                else:
                    #else use the regular portable path
                    p_name = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), 'portable')
            #if os.path.isfile(os.path.join(p_name, "layout.xml")) == False:
                #p_name = os.path.join(os.path.abspath(os.getcwd()), 'portable')
        else:
            p_name = string_wrap(self.sp.GetUserLocalDataDir())
            
        if os.path.isdir(p_name) == False:
            try:
                os.mkdir(p_name)
            except:
                dlg = wx.MessageDialog(self.parent, "Can't create directory\r\n %s" % (p_name), 'Alert', wx.OK | wx.ICON_WARNING)
                if (dlg.ShowModal() == wx.ID_OK):
                    dlg.Destroy()
        return p_name
        
    # --------------------------------------------
        
    def DatabaseLocation(self):
        #sqlite requires utf-8
        dbl = unicode(os.path.join(self.DataDirectory(), 'gravydb.sq3')).encode('utf-8')
        return dbl
        
    def Mp3DataDirectory(self):
        p_name = string_wrap(os.path.join(self.DataDirectory(), 'mp3s'))
        if os.path.isdir(p_name) == False:
            try:
                os.mkdir(p_name)
            except:
                dlg = wx.MessageDialog(self.parent, "Can't create directory\r\n %s" % (p_name), 'Alert', wx.OK | wx.ICON_WARNING)
                if (dlg.ShowModal() == wx.ID_OK):
                    dlg.Destroy()
        return p_name
        
    def MakeDataDirectory(self, dir_name):
        p_name = string_wrap(os.path.join(self.DataDirectory(), dir_name))
        if os.path.isdir(p_name) == False:
            try:
                os.mkdir(p_name)
            except:
                dlg = wx.MessageDialog(self.parent, "Can't create directory\r\n %s" % (p_name), 'Alert', wx.OK | wx.ICON_WARNING)
                if (dlg.ShowModal() == wx.ID_OK):
                    dlg.Destroy()
        return p_name
        
    def Seperator(self):
        return os.sep
        
    def BuildTempFile(self, file_name):
        return os.path.join(self.TempDirectory(), file_name)
       
    def CopyFile(self, file_from, file_to_dir, file_to_name):
        file_name_scrubbed = replace_all(file_to_name)
        file_to = os.path.join(file_to_dir, file_name_scrubbed)
        #print file_from
        #print file_to
        try:
            shutil.copyfile(string_wrap(file_from), string_wrap(file_to))
            return string_wrap(file_to)
        except:
            dlg = wx.MessageDialog(self.parent, "Can't copy file\r\n %s" % file_from, 'Alert', wx.OK | wx.ICON_WARNING)
            if (dlg.ShowModal() == wx.ID_OK):
                dlg.Destroy()

def replace_all(text):
    dic = {'\\':'', '/':'', ':':'', '?':'', '"':'', '<':'', '>':'', '|':'', ' ':'_'}
    #\\/:*?"<>|
    for i, j in dic.iteritems():
        text = text.replace(i, j)
    return text
    
# ===================================================================            
charset = 'utf-8'
        
def string_wrap(s, want_unicode=True):
    """
    
    """
    ##s = s.encode(charset)
    
    if isinstance(s, unicode):
        s = s.encode(charset)
    elif not isinstance(s, str):
        s = str(s)
    #s = urllib.quote(s, safe)
    if want_unicode:
        s = s.decode(charset) # ascii would also work

    return s
# ===================================================================   
