#!/bin/env python
"""
GrooveWalrus: Plug-in Loader
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

#import sqlite3
import  wx
import sys, os

from main_utils.read_write_xml import xml_utils
from main_utils import system_files

SYSLOC = os.path.abspath(os.path.dirname(sys.argv[0])) #os.getcwd()

PLUGINS_LOCATION = SYSLOC + os.sep + "plugins" + os.sep

class PluginLoader():
    #plug-in loader
    def __init__(self, parent):
        self.parent = parent
        self.SETTINGS_LOCATION = system_files.GetDirectories(self).MakeDataDirectory('plugins') + os.sep
        self.LoadPlugins()        
    
    def LoadPlugins(self):
        base_path = self.parent.working_directory + os.sep + "plugins" + os.sep #PLUGINS_LOCATION
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.id_array = {}
        id_counter = 1100
        #accerators
        acc_arr = []
        for root, dirs, files in os.walk(base_path):
            dir_name = root.rsplit(os.sep, 1)[1]
            #print dir_name
            counter = 0
            #counter = counter + files.count("settings_" + dir_name + ".xml")
            counter = counter + files.count("layout_" + dir_name + ".xml")
            counter = counter + files.count("info_" + dir_name + ".xml")
            counter = counter + files.count("icon_" + dir_name + ".png")
            counter = counter + files.count(dir_name + ".py")
            counter = counter + files.count(dir_name + ".pyo")
            
            if counter >= 4:
                #load plugin
                self.id_array[id_counter] = dir_name
                btnsizer = wx.BoxSizer(wx.HORIZONTAL)
    
                # plugin text
                xml_dict = xml_utils().get_generic_settings(root + os.sep + "info_" + dir_name + ".xml")
                hot_key = ''
                if 'title' in xml_dict:
                    t = wx.StaticText(self.parent.pa_options_plugins, -1, xml_dict['title'], size=(120,15), style=wx.ALIGN_RIGHT)
                    font = wx.Font(8, wx.NORMAL, wx.NORMAL, wx.BOLD)
                    t.SetFont(font)
                    btnsizer.Add(t, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
                    hot_key = ' [Alt-' + xml_dict['title'][0] + ']'
                    hot_key_menu = '\t Alt-' + xml_dict['title'][0]
                    acc_arr.append((id_counter, xml_dict['title'][0].upper()))
                
                # plugin button
                bmp = wx.Bitmap(root + os.sep + "icon_" + dir_name + ".png", wx.BITMAP_TYPE_ANY)
                b = wx.BitmapButton(self.parent.pa_options_plugins, id_counter, bmp) #, (20, 20), (bmp.GetWidth()+10, bmp.GetHeight()+10))                
                btnsizer.Add(b, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
                self.parent.Bind(wx.EVT_BUTTON, self.LoadPluginWindow, b)
                    
                if 'description' in xml_dict:
                    d = wx.StaticText(self.parent.pa_options_plugins, -1, xml_dict['description'] + hot_key)
                    btnsizer.Add(d, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
                    
                # sizer
                self.main_sizer.Add(btnsizer, 0, wx.EXPAND|wx.ALL, 0)       
                                
                #add to plug-ins menu
                plugins_menu = self.parent.parent.menu_plugins
                plugins_menu.Append(id_counter, xml_dict['title'])# + hot_key_menu)
                self.parent.parent.Bind(wx.EVT_MENU, self.LoadPluginWindow, id=id_counter)
                
                id_counter = id_counter + 1
                
                #check for autoload
                if self.AutoloadSetting(dir_name):
                    z = self.LoadPluginWindow(None, dir_name)
                    #check to see if it has the ability to add itself as a tab, and do so
                    try:
                        z.OnMakeTabClick()
                    except AttributeError, msg:
                        print msg
                        pass
                
            counter = 0
            
        self.parent.pa_options_plugins.SetSizer(self.main_sizer)
        
        
        #set some more accelerators
        #use the first letter of the plugin + alt for the accerator
        x = self.parent.aTable_values
        for y in acc_arr:               
            #append first letter of plugin and id to accelator table
            x.append((wx.ACCEL_ALT, ord(y[1]), y[0]))        
        aTable = wx.AcceleratorTable(x)
        self.parent.SetAcceleratorTable(aTable)
        self.parent.album_viewer.SetAcceleratorTable(aTable)
        # get a list of directories in the plugins dir
        # check each dir for info.xml
        # read info
        # check for icon.png
        # check for layout_[dirname].xml
        # add gui to plugins tab
        # check db if plugin is active
        
    def LoadPluginWindow(self, event, plugin_name=None):
        #get the button/plugin for the pressed button
        if plugin_name==None:
            plugin_name = self.id_array[event.GetId()]
        #load the plugin 
        exec ("from plugins." + plugin_name + " import " + plugin_name)
        #__import__(plugin_name)
        # show the window
        exec("z= " + plugin_name + ".MainPanel(self.parent)")
        z.Show(True)
        return z
        
    def AutoloadSetting(self, plugin_name):
        #load the setting from settings_[plug-in name].xml if it exists
        settings_dict = xml_utils().get_generic_settings(self.SETTINGS_LOCATION + "settings_" + plugin_name + ".xml")
        autoload=''
        if len(settings_dict) >= 1:
            if settings_dict.has_key('autoload'):
                autoload = int(settings_dict['autoload'])
        return autoload