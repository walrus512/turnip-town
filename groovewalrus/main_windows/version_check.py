"""
GrooveWalrus: Version Check and Update
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

import wx
import xml.etree.ElementTree as ET
import urllib
from main_utils import read_write_xml
import os, sys
import shutil
from main_utils import default_app_open
import wx.xrc as xrc
from threading import Thread
from main_utils import system_files

VERSION_URL = "http://groove-walrus.turnip-town.net/dru/version/version2.xml"
NEWS_URL = "http://groove-walrus.turnip-town.net/dru/version/news2.xml"
FILES_URL = "http://groove-walrus.turnip-town.net/dru/version/files2.xml"
LW = 'http://groove-walrus.turnip-town.net'

SYSLOC = os.path.abspath(os.path.dirname(sys.argv[0]))


class VersionCheck():
    def __init__(self, parent, current_version):
        self.parent = parent
        self.current_version = current_version
    
    def CheckVersion(self):
        tree =''
    	try:
        	url_blob = urllib.urlopen(VERSION_URL)
        	tree = read_write_xml.xml_utils().read_xml_tree(url_blob)
       	except Exception, inst:
       	     print 'Exception: version check: ' + str(inst)
        
        if tree != '':
            root = tree.getroot()            
            # check if remote version number is greater than local version, yes than update icon
            if ( float(root.text) > float(self.current_version) ):
                # display update icon and link
                self.parent.bb_update.Show(True)
                #self.parent.hl_update.Show(True)

    def DisplayNewVersionMessage(self):
    # display a message prompting to update or not
        dlg = UpdateWindow(self.parent, self.current_version).show_me()
                                

UPDATE_RESFILE = os.getcwd() + os.sep + 'layout_update.xml'
        
class UpdateWindow(wx.Dialog):
    """Update Window for updating"""
    def __init__(self, parent, current_version):
        wx.Dialog.__init__(self, parent, -1, "Update", style=wx.FRAME_SHAPED) #STAY_ON_TOP)#wx.FRAME_SHAPED)
        self.parent = parent
        self.current_version = current_version
        
        self.data_directory = system_files.GetDirectories(self.parent).DataDirectory()
        self.update_data_directory = self.data_directory + os.sep + "updates" + os.sep
                        
        # XML Resources can be loaded from a file like this:
        res = xrc.XmlResource(UPDATE_RESFILE)

        # Now create a panel from the resource data
        panel = res.LoadPanel(self, "m_pa_update")

        # control references --------------------
        self.tc_update_text = xrc.XRCCTRL(self, 'm_tc_update_text')
        self.bm_update_close = xrc.XRCCTRL(self, 'm_bm_update_close')
        self.bu_update_update = xrc.XRCCTRL(self, 'm_bu_update_update')
        self.bu_update_restart = xrc.XRCCTRL(self, 'm_bu_update_restart')
        self.st_update_header = xrc.XRCCTRL(self, 'm_st_update_header')

        # bindings ----------------
        self.Bind(wx.EVT_BUTTON, self.OnUpdateClick, id=xrc.XRCID('m_bu_update_update'))
        self.Bind(wx.EVT_BUTTON, self.OnRestartClick, id=xrc.XRCID('m_bu_update_restart'))
        self.Bind(wx.EVT_BUTTON, self.OnWebsiteClick, id=xrc.XRCID('m_bu_update_website'))
        self.bm_update_close.Bind(wx.EVT_LEFT_UP, self.hide_me)
        
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self.st_update_header.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.st_update_header.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.st_update_header.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.st_update_header.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
            
        self.bu_update_restart.Enable(False)    
        # set layout --------------
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel, 1, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.GetNews()
        
#----------------------------------------------------------------------       
    def GetNews(self):
        #read news.xml, print
        tree =''
    	try:
        	url_blob = urllib.urlopen(NEWS_URL)
        	tree = read_write_xml.xml_utils().read_xml_tree(url_blob)
       	except Exception, inst:
       	     print 'Exception: get news: ' + str(inst)
        
        if tree != '':
            root = tree.getroot()            
            self.UpdateTC(root.text)


    def OnUpdateClick(self, event):        
        # check for admin priviliges
        failed = self.CheckAdmin()
                        
        if failed == False:
            # grab the files.xml
            self.bu_update_update.Enable(False)
            self.UpdateTC('reading update list')
            url_blob = urllib.urlopen(FILES_URL)
            tree = read_write_xml.xml_utils().read_xml_tree(url_blob)
            counter = 1
            if tree != '':
                root = tree.getroot()
                sub_root = root.getchildren()            
                file_array = []
                for x in sub_root:
                    # cycle though the files list and grab the update files
                    #print x.tag + ' ' + x.text
                    #dlg2.Update(counter * (100/len(sub_root)))
                    if x.tag == 'file':
                        xdir = x.attrib.get("directory")
                        if xdir == None:
                            xdir =''
                            
                        #get file version info
                        xver = x.attrib.get("version")    
                        if xver == None:
                            xver =''
                        if xver != '':
                            if (float(xver) > float(self.current_version)):
                            #check if we need to make a dir
                                file_array.append((x.text, xdir, xver))                                
                                
            if len(file_array) >= 1:
                self.UpdateTC('update required for %s files' % str(len(file_array)))
                #THREAD
                self.update_thread = UpdateThread(self, self.current_version, file_array, self.data_directory, self.update_data_directory)
                #THREAD
                self.update_thread.start()

    def CheckAdmin(self):
        '''check if you have admin rights'''
        failed = False
        try:
            shutil.copyfile(os.getcwd() + os.sep + 'gw.exe', os.getcwd() + os.sep + 'gw_test.exe')
            os.remove(os.getcwd() + os.sep + 'gw_test.exe')
        except IOError:
            dlg = wx.MessageDialog(self.parent, "Can't copy file!\r\nNeed administrator privileges to update!", 'Alert', wx.OK | wx.ICON_WARNING)
            if (dlg.ShowModal() == wx.ID_OK):
                dlg.Destroy()
            failed = True
        return failed
            
    def OnRestartClick(self, event):
        self.UpdateAndRestart()
        
    def OnWebsiteClick(self, event):
        default_app_open.dopen(LW)
        
    def UpdateTC(self, u_text):
        self.tc_update_text.SetValue(self.tc_update_text.GetValue() + '\r\n...' + u_text)
        
    def GetUpdateFile(self, file_url, file_name, ver_dir):
    # get albumcover for artist/song from last.fm
    # check that file doesn't exist
        urllib.urlretrieve(file_url, self.update_data_directory + ver_dir + file_name)
        urllib.urlcleanup()
        #print 'getting new'
        
    def UpdateAndRestart(self):
    # copy new files
        if os.path.isfile ("gw_upd.exe"):
            os.execv("gw_upd.exe", [])
        else:
            dlg = wx.MessageDialog(self.parent, "Can't find gw_upd.exe\r\nThis is not good.", 'Alert', wx.OK | wx.ICON_WARNING)
            if (dlg.ShowModal() == wx.ID_OK):
                dlg.Destroy()

                
    def show_me(self):
        self.MoveMe()
        self.Show(True) # Shows it        
        
    def MoveMe(self, event=None):
        # show the window
        ps = self.parent.GetSize()
        pp = self.parent.GetScreenPosition()
        ss = self.GetSize()        
        xn = pp[0] + ((ps[0] - ss[0]))
        yn = pp[1] #+ ((ps[1] - ss[1]) / 2)
        self.SetPosition((xn, yn))
        self.SetSize((ss[0], ps[1]))
        
    def hide_me(self, event=None):
        # hide the window
        self.Show(False)         
# --------------------------------------------------------- 
# titlebar-like move and drag
    
    def OnMouseLeftDown(self, evt):
        self.Refresh()
        self.ldPos = evt.GetEventObject().ClientToScreen(evt.GetPosition())
        self.wPos = self.ClientToScreen((0,0))
        self.CaptureMouse()

    def OnMouseMotion(self, evt):
        if evt.Dragging() and evt.LeftIsDown():
            dPos = evt.GetEventObject().ClientToScreen(evt.GetPosition())
            #nPos = (self.wPos.x + (dPos.x - self.ldPos.x), -2)
            nPos = (self.wPos.x + (dPos.x - self.ldPos.x), self.wPos.y + (dPos.y - self.ldPos.y))
            self.Move(nPos)
            #try:
            #    self.popup.IsShown()
            #except AttributeError:
            #    pass
            #else:
            #    if (self.popup.IsShown()):
            #        pPos = (self.wPos.x + (dPos.x - self.ldPos.x),34)
             #       self.popup.Move(pPos)

    def OnMouseLeftUp(self, evt):
        try:
            self.ReleaseMouse()
        except wx._core.PyAssertionError:
            pass

    def OnRightUp(self, evt):
        self.hide_me()
        #self..Destroy()
        
# --------------------------------------------------------- 

#---------------------------------------------------------------------------
# ####################################
class UpdateThread(Thread): 
    # grab rss feeds, thread style  
    def __init__(self, parent, current_version, file_array, data_directory, update_data_directory):
        Thread.__init__(self)
        self.parent = parent
        self.current_version = current_version 
        self.file_array = file_array
        self.data_directory = data_directory
        self.update_data_directory = update_data_directory
         
    def run(self):        
        #create dirs
        
        #create update dirs
        for x in self.file_array:
            #x.text, xdir, xver | file_name, directory, version
            proceed = self.CreateDir(self.update_data_directory, x[2])
            if proceed == True:
                base = self.update_data_directory + x[2] + os.sep
                directory = x[1]                
                if (self.CreateDir(base, directory) != True):
                    proceed = False
                    break
        #create regular program dirs
        if proceed == True:
        #create update dirs
            for x in self.file_array:
                #x.text, xdir, xver
                base = self.data_directory + os.sep
                directory = x[1]
                if (self.CreateDir(base, directory) != True):
                    proceed = False
                    break
        #download files
        if proceed == True:
            self.parent.UpdateTC('downloading files')
            for x in self.file_array:
                file_name = x[0].rsplit("/", 1)[1]
                version_dir = x[2] + os.sep + x[1]
                if x[1] != '':
                    version_dir = x[2] + os.sep + x[1] + os.sep
                self.parent.GetUpdateFile(x[0], file_name, version_dir)
                self.parent.UpdateTC('downloading: %s' % file_name)
        #copy files
        if proceed == True:
        #create update dirs
            self.parent.UpdateTC('copying files')
            for x in self.file_array:
                #x.text, xdir, xver                
                directory = ''
                if len(x[1]) >= 1:
                    directory = x[1] + os.sep
                from_dir = self.update_data_directory + x[2] + os.sep + directory
                #to_dir = self.data_directory + os.sep + directory
                to_dir = SYSLOC + os.sep + directory                
                file_name = x[0].rsplit("/", 1)[1]
                self.parent.UpdateTC('copying: %s' % file_name)
                if (self.CopyFile(file_name, from_dir, to_dir) != True):
                    proceed = False
                    break            
        #restart
        if proceed == True:
            self.parent.UpdateTC('update complete')
            self.parent.UpdateTC('click Restart to restart GrooveWalrus')
            wx.Log.EnableLogging(False)
            self.parent.bu_update_restart.Enable(True)
        
    def CopyFile(self, file_name, from_dir, to_dir):
        status = True
        if file_name == 'gw.exe':
            try:
                shutil.copyfile(from_dir + file_name, to_dir + 'gw_upd.exe')                                        
            except:
                dlg = wx.MessageDialog(self.parent, "Can't copy file\r\n %s" % file_name, 'Alert', wx.OK | wx.ICON_WARNING)
                if (dlg.ShowModal() == wx.ID_OK):
                    dlg.Destroy()
                    status = False
                    self.parent.UpdateTC('error: copying file: %s' % (from_dir + file_name))
        else:
            try:
                shutil.copyfile(from_dir + file_name, to_dir + file_name)
            except:
                dlg = wx.MessageDialog(self.parent, "Can't copy file\r\n %s" % file_name, 'Alert', wx.OK | wx.ICON_WARNING)
                if (dlg.ShowModal() == wx.ID_OK):
                    dlg.Destroy()
                    status = False
                    self.parent.UpdateTC('error: copying file: %s' % (from_dir + file_name))
                    
        return status
        
    def CreateDir(self, base, directory):
        status = True    
        if os.path.isdir(base + directory) == False:
            self.parent.UpdateTC('creating directory: %s' % directory)
            
            #check for somedir/subdir
            if len(directory.split('/')) > 1:            
                #assume 2 levels for now
                first_dir = directory.split('/')[0]
                directory = directory.replace('/', os.sep)                
                if os.path.isdir(base + first_dir) == False:
                    try:
                        os.mkdir(base + first_dir)
                    except:
                        dlg = wx.MessageDialog(self.parent, "Can't create directory\r\n %s" % (base + first_dir), 'Alert', wx.OK | wx.ICON_WARNING)
                        if (dlg.ShowModal() == wx.ID_OK):
                            dlg.Destroy()
                            status = False
                            self.parent.UpdateTC('error: creating directory: %s' % (base + first_dir))
            try:
                os.mkdir(base + directory)
            except:
                dlg = wx.MessageDialog(self.parent, "Can't create directory\r\n %s" % (base + directory), 'Alert', wx.OK | wx.ICON_WARNING)
                if (dlg.ShowModal() == wx.ID_OK):
                    dlg.Destroy()
                    status = False
                    self.parent.UpdateTC('error: creating directory: %s' % (base + directory))
        return status
        
