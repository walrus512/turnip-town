"""
GrooveWalrus: Version Updater
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

import wx
#import wx.html
import wx.xrc as xrc

import os
import sys

import urllib
import zipfile
import hashlib
import subprocess

from threading import Thread

from main_utils import default_app_open
from main_utils import read_write_xml
from main_utils import system_files

PROGRAM_VERSION = "0.001"
PROGRAM_NAME = "Version Update"


##if sys.argv[-1][0:2] == 'v=':
    #killing the process also kills the cwd, we must rebuild it
    #C:\ProgramFiles(x86)\GrooveWalrus\version_update.exe v=0.213
    #yy = ''
    #for xx in range (0, (len(sys.argv)-1)):
    #    yy = yy + sys.argv[xx]
    #SYSLOC = yy.rsplit(os.sep, 1)[0]
##    SYSLOC = os.getcwd()
##else:
##    SYSLOC = os.path.abspath(os.path.dirname(sys.argv[0])) 

SYSLOC = os.path.abspath(os.path.dirname(sys.argv[0]))
if os.path.isfile(SYSLOC + os.sep + "layout.xml") == False:
    SYSLOC = os.path.abspath(os.getcwd())
    
GRAPHICS_LOCATION = os.path.join(SYSLOC, 'graphics') + os.sep

RESFILE = os.getcwd() + os.sep + 'layout_version_update.xml'


class MyApp(wx.App):

    def OnInit(self):
        self.res = xrc.XmlResource(RESFILE)
        self.init_frame(current_version=None)
        return True

    def init_frame(self, current_version):
        frame = self.res.LoadFrame(None, 'm_fr_main')
        self.frame = frame
        
        self.current_version = current_version
        
        self.data_directory = system_files.GetDirectories(self).DataDirectory()
        self.update_data_directory = self.data_directory + os.sep + "updates" + os.sep
                            
        frame.SetTitle(PROGRAM_NAME + ' ' + PROGRAM_VERSION)
        
        # control references --------------------
        frame.lb_main = xrc.XRCCTRL(frame, 'm_lb_main')
        frame.tc_version = xrc.XRCCTRL(frame, 'm_tc_version')
        frame.tc_files = xrc.XRCCTRL(frame, 'm_tc_files')
        frame.tc_news = xrc.XRCCTRL(frame, 'm_tc_news')
        frame.tc_website = xrc.XRCCTRL(frame, 'm_tc_website')
        frame.tc_news_text = xrc.XRCCTRL(frame, 'm_tc_news_text')
        frame.bu_update = xrc.XRCCTRL(frame, 'm_bu_update')
        frame.bu_restart = xrc.XRCCTRL(frame, 'm_bu_restart')
        
        frame.tc_local_dir = xrc.XRCCTRL(frame, 'm_tc_local_dir')
        frame.tc_update_dir = xrc.XRCCTRL(frame, 'm_tc_update_dir')
        
        frame.tc_local_dir.SetValue(SYSLOC)
        frame.tc_update_dir.SetValue(self.update_data_directory)
        
        # bindings ----------------
        frame.Bind(wx.EVT_BUTTON, self.OnUpdateClick, id=xrc.XRCID('m_bu_update'))
        frame.Bind(wx.EVT_BUTTON, self.OnRestartClick, id=xrc.XRCID('m_bu_restart'))
        frame.Bind(wx.EVT_MENU, self.OnAboutClick, id=xrc.XRCID("m_mi_about"))
        frame.Bind(wx.EVT_MENU, self.OnExitClick, id=xrc.XRCID("m_mi_exit"))

        #listbook images ------
        ##il = wx.ImageList(32, 32, True)        
        ##image_files = [
        ##    GRAPHICS_LOCATION + 'network-workgroup-32.png', 
        ##    GRAPHICS_LOCATION + 'preferences-system-32.png'
            #GRAPHICS_LOCATION + 'weather-overcast.png', 
            #GRAPHICS_LOCATION + 'weather-few-clouds.png', 
            #GRAPHICS_LOCATION + 'weather-clear.png'
        ##    ]            
        ##for file_name in image_files:
        ##    bmp = wx.Bitmap(file_name, wx.BITMAP_TYPE_PNG)
        ##    il.Add(bmp)
        ##frame.lb_main.AssignImageList(il)
        ##frame.lb_main.SetPageImage(0, 0)
        ##frame.lb_main.SetPageImage(1, 1)
        
        # get current version -----
        # current version is either passed from the command line
        #  or called directly
        if self.current_version == None:
            if sys.argv[-1][0:2] == 'v=':
                self.current_version = sys.argv[-1][2:]
        #print self.current_version

        # load settings -----
        self.settings_dict = read_write_xml.xml_utils().get_generic_settings('version_update_settings.xml')
        frame.tc_version.SetValue(self.settings_dict['version'])
        frame.tc_news.SetValue(self.settings_dict['news'])
        frame.tc_files.SetValue(self.settings_dict['files'])
        frame.tc_website.SetValue(self.settings_dict['website'])
        
        # load news.xml -----
        self.GetNews()
        
        # update text
        self.current_text = """========
Updating
========
"""
        
        frame.Show(True)
        #y=''
        #for x in sys.argv:
        #    y = y + x
        #dlg = wx.MessageDialog(frame, y+str(len(sys.argv)), 'Alert', wx.OK | wx.ICON_WARNING)
        #if (dlg.ShowModal() == wx.ID_OK):
        #    dlg.Destroy()
    
    def OnExitClick(self, event=None):
        self.frame.Destroy()
        #sys.exit()#1
        #os._exit()#2
        
#----------------------------------------------------------------------       
    def GetNews(self):
        #read news.xml, print
        tree =''
    	try:
        	url_blob = urllib.urlopen(self.settings_dict['news'])
        	tree = read_write_xml.xml_utils().read_xml_tree(url_blob)
       	except Exception, inst:
       	     print 'Exception: get news: ' + str(inst)
        
        if tree != '':
            root = tree.getroot()    
            self.news_html = root.text #.replace('[', '<')
            #self.news_html = self.news_html.replace(']', '>')
            #self.UpdateTC(root.text)
            #page_contents = '<p><FONT SIZE=3><b>' + unicode(artist) + '</b></FONT><br><br><FONT SIZE=-1>' + unicode(bio_text_str) + '</FONT></p>'
            self.frame.tc_news_text.SetValue(self.news_html)
   
    def OnUpdateClick(self, event):        
        # check for admin priviliges
        failed = False #self.CheckAdmin()
                        
        if failed == False:
            # grab the files.xml
            self.frame.bu_update.Enable(False)
            self.UpdateTC('reading update list')
            url_blob = urllib.urlopen(self.settings_dict['files'])
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
                        #xdir = x.attrib.get("directory")
                        #if xdir == None:
                        #    xdir =''                            
                        xsha1 = x.attrib.get("sha1")
                        if xsha1 == None:
                            xsha1 =' '                                                
                        xver = x.attrib.get("version")    
                        if xver == None:
                            xver =' '                        
                        if xver != '':
                            try:
                                if (float(xver) > float(self.current_version)):
                                    file_array.append((x.text, xsha1, xver))
                            except Exception, inst:
                                self.UpdateTC('failed: can\'t find versions.')
                            
            if len(file_array) >= 1:
                self.UpdateTC('update required for %s file(s)' % str(len(file_array)))
                #THREAD
                self.update_thread = UpdateThread(self, self.current_version, file_array, self.data_directory, self.update_data_directory)
                #THREAD
                self.update_thread.start()
            else:
                self.UpdateTC('no update required')

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
        default_app_open.dopen(self.settings_dict['website'])
        
    def UpdateTC(self, u_text):
        self.current_text = self.current_text + '...' + u_text + '\r\n'
        out_text = self.current_text + '\r\n' + self.news_html
        self.frame.tc_news_text.SetValue(out_text)
        #pass
        #self.tc_update_text.SetValue(self.tc_update_text.GetValue() + '\r\n...' + u_text)
        
    def GetUpdateFile(self, file_url, file_name, ver_dir, file_size):
    # grab a file
        local_file =  self.update_data_directory + ver_dir + file_name
        #dlg = wx.ProgressDialog("File Download", file_name, maximum = file_size,
        #               parent=self.frame, style = wx.PD_CAN_ABORT | wx.PD_APP_MODAL | wx.PD_ELAPSED_TIME )        
        urllib.urlretrieve(file_url, local_file)
        #sz = os.path.getsize(local_file)
        #dlg.Update(sz)
        #dlg.Destroy()
        urllib.urlcleanup()
        #print 'getting new'
        return local_file
        
    def UpdateAndRestart(self):
    # restart main program
        sys.stdout.flush()
        if os.path.isfile (SYSLOC + os.sep + "gw.exe"):
            program = SYSLOC + os.sep + "gw.exe"
            arguments = []
            os.execvp(program, (program,) +  tuple(arguments))
            #self.frame.Destroy()
            self.KillCurrent()
        elif os.path.isfile (SYSLOC + os.sep + "gw.py"):            
            child = subprocess.Popen("python gw.py")
            #self.frame.Destroy()
            self.KillCurrent()
            #if os.name == 'nt':
            #    os.execvp("gw.py", [])
            #else:
            #    os.execvp("python", ['gw.py'])
        else:
            dlg = wx.MessageDialog(self.parent, "Can't find gw.exe/gw.py\r\nThis is not good.", 'Alert', wx.OK | wx.ICON_WARNING)
            if (dlg.ShowModal() == wx.ID_OK):
                dlg.Destroy()
       
    def KillCurrent(self):
        sys.exit()#1
        os._exit()#2
# --------------------------------------------------------- 
    def OnAboutClick(self, event):
        # First we create and fill the info object
        info = wx.AboutDialogInfo()
        info.Name = PROGRAM_NAME
        info.Version = PROGRAM_VERSION
        info.Copyright = "(c) 1906 - 2018"
        info.Description = """
Products Used
==========
Tango Icons - http://tango.freedesktop.org
"""
        info.WebSite = ("http://groove-walrus.turnip-town.net", "http://groove-walrus.turnip-town.net")

        # Then we call wx.AboutBox giving it that info object
        wx.AboutBox(info)


# --------------------------------------------------------- 

#---------------------------------------------------------------------------
# ####################################
# check files.xml, get zip file and checksum
# download zip file
# checksum zip file
# extract zip file to updates dir
# copy updates to groovewalrus install dir, overwriting
#<file version="0.201" hash="g42g324g34g34g">http://groove-walrus.turnip-town.net/dru/version/files/0210_update.zip</file>

class UpdateThread(Thread): 
    # update files, thread style  
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
            #if proceed == True:
                #base = self.update_data_directory + x[2] + os.sep
                #directory = x[1]
                #if (self.CreateDir(base, directory) != True):
                #    proceed = False
                #    break
        #create regular program dirs
        #if proceed == True:
        #create update dirs
            #for x in self.file_array:
                #x.text, xsha1, xver
                #base = self.data_directory + os.sep
                #directory = x[1]
                #if (self.CreateDir(base, directory) != True):
                #    proceed = False
                #    break
        #download files
        if proceed == True:
            self.parent.UpdateTC('downloading files')
            for x in self.file_array:
                file_name = x[0].rsplit("/", 1)[1]
                sha1_check = x[1]
                version_dir = x[2] + os.sep #+ x[1]
                #print file_name
                #print version_dir
                #if x[1] != '':
                    #version_dir = x[2] + os.sep + x[1] + os.sep
                
                # check the server has a zip to download
                f = urllib.urlopen(x[0])
                y = f.info()
                if y.items().count(('content-type', 'application/x-zip')) == 0:                
                    proceed = False
                    self.parent.UpdateTC("Can't find: %s on remote server." % file_name)
                    break
                download_size = 0
                for headers in y.items():
                    if headers[0] == 'content-length':
                        download_size = int(headers[1])
                        break
                #print download_size
                #Content-Length: 543
                #Content-Type: application/x-zip
                #Content-Disposition: attachment; filename="gw_0216_update.zip"
                
                self.parent.UpdateTC('downloading: %s' % file_name)                
                local_file = self.parent.GetUpdateFile(x[0], file_name, version_dir, download_size)
                
                #check sha1 of downloaded file
                self.parent.UpdateTC('checking SHA1: %s' % file_name)
                if CheckSha1(local_file, sha1_check) == False:
                    proceed = False
                    self.parent.UpdateTC("SHA1 failed: %s" % file_name)
                    break
                #unzip file
                if proceed == True:
                    self.parent.UpdateTC('unzipping: %s' % file_name)
                    self.parent.UpdateTC('to: %s' % SYSLOC + os.sep)
                    self.UnzipFile(local_file, SYSLOC + os.sep)
        #copy files
        #if proceed == True:
        #create update dirs
            #self.parent.UpdateTC('copying files')
            #for x in self.file_array:
                #x.text, xdir, xver                
             #   directory = ''
              #  if len(x[1]) >= 1:
               #     directory = x[1] + os.sep
               # from_dir = self.update_data_directory + x[2] + os.sep + directory
                #to_dir = self.data_directory + os.sep + directory
           #     to_dir = SYSLOC + os.sep + directory                
            #    file_name = x[0].rsplit("/", 1)[1]
             #   self.parent.UpdateTC('copying: %s' % file_name)
              #  if (self.CopyFile(file_name, from_dir, to_dir) != True):
               #     proceed = False
                #    break            
        #restart
        if proceed == True:
            self.parent.UpdateTC('update complete')
            self.parent.UpdateTC('click Restart to restart the program')
            #wx.Log.EnableLogging(False)
            self.parent.frame.bu_restart.Enable(True)
        
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
        
    def UnzipFile(self, zip_file_name, extract_to):
    
        if zipfile.is_zipfile(zip_file_name):
            
            # open the zipped file
            zfile = zipfile.ZipFile(zip_file_name, "r")
            
            if zfile.testzip() == None:
            
                #zfile.printdir()
                
                # get each archived file and process the decompressed data
                for info in zfile.infolist():
                    fname = info.filename
                    # decompress each file's data
                    data = zfile.read(fname)
                    
                    # save the decompressed data to a new file
                    filename = extract_to + fname
                    if filename[-1] == '/':
                        #it's a directory
                        self.CreateDir(extract_to, fname)
                    else:
                        #it's a file
                        fout = open(filename, "wb")
                        fout.write(data)
                        fout.close()
                        self.parent.UpdateTC('extracted: ' + fname)
            else:
                self.parent.UpdateTC('failed test zipfile: ' + zip_file_name)
        else:
            self.parent.UpdateTC('not zipfile: ' + zip_file_name)

# ----------------------------------------------------
# ----------------------------------------------------

def CheckSha1(local_file, sha1_check):
    #checks the sha1 of a local file to one provided
    x = hashlib.sha1()
    file_ob = open(local_file, 'rb')
    x.update(file_ob.read())
    fd = x.hexdigest()
    
    if fd == sha1_check:
        return(True)
    else:
        return(False)

#---------------------------------------------------------------------------
#---------------------------------------------------------------------------

    #app = wx.PySimpleApp()
    #LoadMain()
    #app.MainLoop() 
      
if __name__ == '__main__':
    app = MyApp(False)
    app.MainLoop()



