#! /usr/bin/env python
import codecs
import os
import shutil
import sys
from xml.etree import ElementTree

import msgfmt

__version__ = '0.1'

header = """
msgid ""
msgstr ""
"Project-Id-Version: PACKAGE VERSION\\n"
"POT-Creation-Date: Fri Feb 18 16:51:55 2005\\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"
"Language-Team: LANGUAGE <LL@li.org>\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=CHARSET\\n"
"Content-Transfer-Encoding: ENCODING\\n"
"Generated-By: xrc_i18n.py\\n"

"""

def extractIds(filename):
    result = []
    
    tree = ElementTree.parse(filename).getroot()
    #print tree.text
    print tree.getiterator('{http://www.wxwindows.org/wxxrc}label')
    
    tags = [
        '{http://www.wxwindows.org/wxxrc}label',
        #'label',
        '{http://www.wxwindows.org/wxxrc}item',
        '{http://www.wxwindows.org/wxxrc}tooltip',
        '{http://www.wxwindows.org/wxxrc}title'
    ]
    
    for tag in tags:
        for elm in tree.getiterator(tag):
            print elm
            if elm.text not in result:
                result.append(elm.text)
    return result

def makePOT(msgIds, filename):
    makeBackup(filename)
    
    of = file(filename, 'w')
    of.write(header)
    for id in msgIds:
        of.write ('msgid "%s"\n' % id)
        of.write ('msgstr ""\n\n')

    of.close()
    
    
def syncPO(msgIds, filename):
    content = {}
    ifn = codecs.open(filename, 'r')
    for line in ifn:
        if line[0:5] == 'msgid':
            kstr = line.find('"')
            kend = line.rfind('"')
            key = line[ kstr + 1 : kend]
        elif line [0:5] == 'msgst':
            mstr = line.find('"')
            mend = line.rfind('"')
            msg = line[ mstr + 1 : mend]
            
            content[key] = msg
            
    ifn.close()
    
    makeBackup(filename)
    
    of = codecs.open(filename, 'w')
    of.write(header)
    
    for id in msgIds:
        of.write ('msgid "%s"\n' % id)
        if content.has_key(id):
            of.write ('msgstr "%s"\n\n' % content[id])
        else:
            of.write ('msgstr ""\n\n')
    of.close()
    
def makeMO(poPath):
    moPath = poPath[ 0 : poPath.rfind('.')] + '.mo'
    msgfmt.make(poPath, moPath)
                
def getPOs(path):
    out = []
    for item in os.listdir(path):
        fullpath = os.path.join(path, item)
        if os.path.isdir(fullpath):
            res = getPOs(fullpath)
            out += res
        elif os.path.isfile(fullpath) and item[item.rfind('.') + 1 :] == 'po':    
            out.append(fullpath)
    return out
            
def makeBackup(filename):             
    id = 1
    while True:
        nfilename = '%s.%d.bak' % (filename, id)
        if not os.path.exists(nfilename):
            shutil.copy(filename, nfilename)
            break;
        id += 1

def usage():
    print 'python xrc_i18n.py xrc_filename localepath'

def main():
    if len (sys.argv) < 3:
        usage()
        sys.exit(1)
    
    xrcpath = sys.argv[1]
    localepath = sys.argv[2]
    
    if not os.path.isfile(xrcpath):
        print 'File %s does not exist' % xrcpath
        usage()
        sys.exit(1)
    
    if not os.path.isdir(localepath):
        print 'Problem with directory %s' % localepath
        usage()
        sys.exit(1)
    
    potpath = os.path.join(localepath, ".".join( xrcpath.split('.')[:-1] + ['pot'] ))
    
    print 'Extracting messages from XRC file'
    msgIds = extractIds(xrcpath)
    print ' - Done'
    print 'Creating POT file'
    makePOT(msgIds, potpath)
    print ' - Done'
    pos = getPOs(localepath)
    print 'Syncing PO files'
    for fn in pos:
        syncPO(msgIds, fn)
    print ' - Done'
    print 'Compiling MO files'
    for fn in pos:
        makeMO(fn)
    print ' - Done'

if __name__ == '__main__':
    main()
