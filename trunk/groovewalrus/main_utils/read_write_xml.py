"""
GrooveWalrus: Read/Write XML
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

import xml.etree.ElementTree as ET
import os

class xml_utils():
    # xml file junk for hippies
    def __init__(self):
        pass
    
    def write_xml_tree(self, tree, file_name):
        # takes whatever ET xml blob you shove at and saves it
        # *** doesn't write the xml header, worry about that if nesscessary later
        #encoding='utf-8'
        tree.write(file_name)              
    
    def read_xml_tree(self, file_name):
        # reads in an xml file and returns a blob for you to work with
        try:
            tree = ET.parse(file_name)
            print file_name
        except IOError:
            tree = ''
            print 'error:read_xml_tree'
        return tree
    
    def get_tracks(self, file_name):
        # returns array with feed infomation, 3 values for each feed
    
        tree = self.read_xml_tree(file_name)

        track_list = []
        if tree != '':
            root = tree.getroot()
            #if the xml file has xmlns attribute, elementtree likes to magically qualify all the tags with that ns
            #{http://xspf.org/ns/0/}playlist
            root_tag = root.tag
            namespace = ''
            if len(root_tag.split('}')) > 1:
                namespace = root_tag.split('}')[0] + '}'
                
            #sub_root = root.getchildren()
            iter = tree.getiterator(namespace + 'track')            
            # check if there's a feed
            if (len(iter) > 0):              
                if (len(iter[0]) == 5):
                    for x,y,z,c, d in iter:
                    # only add active feeds
                        track_list.append({x.tag.split('}')[-1]: x.text, y.tag.split('}')[-1]: y.text, z.tag.split('}')[-1]: z.text, c.tag.split('}')[-1]: c.text, d.tag.split('}')[-1]: d.text})
        return track_list
        
    def save_tracks(self, file_name, feed_data):
        # make xml file with array with feed infomation, 3 values for each feed
        root = ET.Element("playlist", version="1", xmlns="http://xspf.org/ns/0/")
        tracklist = ET.SubElement(root, "trackList")
        # *** fix so it just cycles throw array keys too, instead of explicitly sating them
        for x in feed_data:            
            feed = ET.SubElement(tracklist, "track")
            name = ET.SubElement(feed, "creator")
            name.text = x['creator']
            url = ET.SubElement(feed, "title")
            url.text = x['title']
            alb = ET.SubElement(feed, "album")
            alb.text = x['album']
            sid = ET.SubElement(feed, "location")
            sid.text = x['location']
            dur = ET.SubElement(feed, "duration")
            dur.text = x['duration']
            
        tree = ET.ElementTree(root)         
        #pretty_tree = ET.tostring(root).replace('><', '>\r\n<')
        #print pretty_tree
        self.write_xml_tree(tree, file_name)
        return "Saved"
        
# ---------------------------------------------------------------        
    def get_generic_settings(self, file_name):
        # gets settings from window settings file returns an object / settings
        window_dict = {}
        if (os.path.isfile(file_name)):
            tree = self.read_xml_tree(file_name)

            # make a blob of settings info
            root = tree.getroot()            

            for x in root:
                # makes a dictionary with xml tag / value pairs
                sub_list = []
                window_dict[x.tag] = x.text
                #print ET.tostring(x)
            
                # drill down another layer
                sub_root = x.getchildren()
                #print sub_root
                for y in sub_root:
            	    sub_list.append(y.text)
            	    #print sub_list
            	    window_dict[y.tag] = sub_list     
        
        else:
            pass
            
        return window_dict
        
    def save_generic_settings(self, path, file_name, data_dict):
        # generate and save simple xml file
        root = ET.Element(file_name.split('.')[0])        
        for x in data_dict:
            #print x
            #print data_dict[x]
            tag = ET.SubElement(root, x)
            tag.text = data_dict[x]
            
        tree = ET.ElementTree(root)         
        
        #print tree
        self.write_xml_tree(tree, path + file_name)
        return "Saved"
        
#<?xml version="1.0" encoding="UTF-8"?>     
#<playlist version="1">
#  <trackList>
#    <track>
#      <title>Believe</title>
#      <album>Believe</album>
#      <creator>Cher</creator>
#      <duration>240000</duration>
#      <location>http://grooveshark.com/id</location>
#    </track>
#  </trackList>
#</playlist>
        
