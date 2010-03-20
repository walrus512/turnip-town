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
#import os.path
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
        
    def DataDirectory(self):
        u_dir = string_wrap(self.sp.GetUserDataDir())
        if os.path.isdir(u_dir) == False:
            try:
                os.mkdir(u_dir)
            except:
                dlg = wx.MessageDialog(self.parent, "Can't create directory\r\n %s" % (u_dir), 'Alert', wx.OK | wx.ICON_WARNING)
                if (dlg.ShowModal() == wx.ID_OK):
                    dlg.Destroy()
        
        return u_dir
        #return self.sp.GetUserDataDir()
        
    def Mp3DataDirectory(self):
        p_name = string_wrap(self.sp.GetUserDataDir() + self.Seperator() + 'mp3s')
        if os.path.isdir(p_name) == False:
            try:
                os.mkdir(p_name)
            except:
                dlg = wx.MessageDialog(self.parent, "Can't create directory\r\n %s" % (p_name), 'Alert', wx.OK | wx.ICON_WARNING)
                if (dlg.ShowModal() == wx.ID_OK):
                    dlg.Destroy()
        return p_name
        
    def MakeDataDirectory(self, dir_name):
        p_name = string_wrap(self.sp.GetUserDataDir() + self.Seperator() + dir_name)
        if os.path.isdir(p_name) == False:
            try:
                os.mkdir(p_name)
            except:
                dlg = wx.MessageDialog(self.parent, "Can't create directory\r\n %s" % (p_name), 'Alert', wx.OK | wx.ICON_WARNING)
                if (dlg.ShowModal() == wx.ID_OK):
                    dlg.Destroy()
        return p_name
        
    def TempDirectory(self):
        p_name = string_wrap(self.sp.GetUserLocalDataDir())
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
        return self.TempDirectory() + self.Seperator() + file_name
       
    def CopyFile(self, file_from, file_to_dir, file_to_name):
        file_name_scrubbed = replace_all(file_to_name)
        file_to = file_to_dir + self.Seperator() + file_name_scrubbed
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
