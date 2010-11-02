# Requires wxPython.  This sample demonstrates:
#
# - single file exe using wxPython as GUI.

from distutils.core import setup
import py2exe
import sys

import glob #matplot
import matplotlib


# If run without args, build executables, in quiet mode.
if len(sys.argv) == 1:
    sys.argv.append("py2exe")
    sys.argv.append("-q")

class Target:
    def __init__(self, **kw):
        self.__dict__.update(kw)
        # for the versioninfo resources
        self.version = "0.324"
        self.company_name = "Turnip-Town.net"
        self.copyright = "lots of copyright"
        self.name = "GrooveWalrus"

################################################################
# A program using wxPython

# The manifest will be inserted as resource into test_wx.exe.  This
# gives the controls the Windows XP appearance (if run on XP ;-)
#
# Another option would be to store it in a file named
# test_wx.exe.manifest, and copy it with the data_files option into
# the dist-dir.
#
manifest_template = '''
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
<assemblyIdentity
    version="5.0.0.0"
    processorArchitecture="x86"
    name="%(prog)s"
    type="win32"
/>
<description>%(prog)s Program</description>
<dependency>
    <dependentAssembly>
        <assemblyIdentity
            type="win32"
            name="Microsoft.Windows.Common-Controls"
            version="6.0.0.0"
            processorArchitecture="X86"
            publicKeyToken="6595b64144ccf1df"
            language="*"
        />
    </dependentAssembly>
</dependency>
</assembly>
'''

RT_MANIFEST = 24

test_wx = Target(
    # used for the versioninfo resource
    description = "GrooveWalrus",

    # what to build
    script = "gw.py",
    other_resources = [(RT_MANIFEST, 1, manifest_template % dict(prog="test_wx"))],
    icon_resources = [(0, "gw7.ico")],
    dest_base = "gw")

################################################################

#includes = ["_mysql","MySQLdb","_mysql_exceptions",]
#includes = ["comtypes"]
includes = ["email.iterators",]
excludes = ['_tkinter', '_gtkagg', '_tkagg', '_agg2', '_cairo',
            'QtCore','QtGui','Tkinter','Tkconstants',
            '_cocoaagg', '_fltkagg', '_gtk', '_gtkcairo', ]

setup(
    options = {"py2exe": {###"compressed": 1,
                          "optimize": 2,
                          "packages": ["encodings"],
                          "includes": includes,
                          "excludes": excludes, #matplot
                          'dll_excludes': ['tk84.dll', 'tcl84.dll', 'libgdk-win32-2.0-0.dll', 'libgobject-2.0-0.dll', 'libglib-2.0-0.dll', 'libgthread-2.0-0.dll'],
                          ###"bundle_files": 3
                          "skip_archive": 1 ###
                          }},                          
                          # 1 - bundles all into zip
                          # 2 - all but python.dll
                          # 3 - none
    # zipfile = None,
    # zip file = none compacts it into the exe
    data_files = matplotlib.get_py2exe_datafiles(),
    windows = [test_wx],
    )
    
import shutil

#shutil.rmtree('./dist/tcl')
shutil.rmtree('./build')
shutil.rmtree('./dist/mpl-data/example')
shutil.rmtree('./dist/mpl-data/images')
