"""
GrooveWalrus: Download Feed
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

import urllib
#import xml.etree.ElementTree as ET
from main_thirdp.beautifulsoup import BeautifulStoneSoup

def read_xml_tree(feed_location):
    # reads in an xml file and returns a blob for you to work with
    tree = ''
    try:
        ###tree = ET.parse(urllib.urlopen(feed_location))
        tree = BeautifulStoneSoup(urllib.urlopen(feed_location))
    except Exception, inst:
         print 'Exception: rss: ' + str(inst)        
    return tree
    
def GetRSSFeed(feed_location):
    # get remote feed and parse 
    # beautiful soup   
    rss_list = []
    item_count = 0
    
    tree = read_xml_tree(feed_location)
    items = tree.findAll('item')
    for titles in items:
        title = titles.findAll('title')
        text_out = CleanText(title[0].string)
        rss_list.append(text_out)        
    
    return rss_list

def GetRSSFeed2(feed_location):
    # get remote feed and parse
    # elemetree    
    rss_list = []
    item_count = 0
    
    tree = read_xml_tree(feed_location)
    if tree != '':
        root = tree.getroot()
        #if the xml file has xmlns attribute, elementtree likes to magically qualify all the tags with that ns
        #{http://xspf.org/ns/0/}playlist
        root_tag = root.tag
        namespace = ''
        if len(root_tag.split('}')) > 1:
            namespace = root_tag.split('}')[0] + '}'            

        iter = tree.getiterator(namespace + 'item')
        # check if there's a feed
        for x in iter:
            iter2 = x.getiterator(namespace + 'title')            
            for y in iter2:
                text_out = CleanText(y.text) 
                rss_list.append(text_out) 
        
        return rss_list
   
#------------    
def CleanText(text):
    text = text.strip()
    text = text.replace('\r\n', '')
    text = text.replace('\n', '')
    text = text.replace('  ', ' ')
    text = text.replace('&amp;', '&')
    #text = url_quote(text)
    return text
    
    
#------------
charset = 'utf-8'
        
def url_quote(s, safe='/', want_unicode=False):
    """
    Wrapper around urllib.quote doing the encoding/decoding as usually wanted:
    
    @param s: the string to quote (can be str or unicode, if it is unicode,
              config.charset is used to encode it before calling urllib)
    @param safe: just passed through to urllib
    @param want_unicode: for the less usual case that you want to get back
                         unicode and not str, set this to True
                         Default is False.
    """
    if isinstance(s, unicode):
        s = s.encode(charset)
    elif not isinstance(s, str):
        s = str(s)
    #s = urllib.quote(s, safe)
    if want_unicode:
        s = s.decode(charset) # ascii would also work
    return s
 


