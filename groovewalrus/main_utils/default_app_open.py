#!/usr/bin/env python

'''Utilities for opening files or URLs in the registered default application
and for sending e-mail using the user's preferred composer.
http://code.activestate.com/recipes/511443/
'''

__version__ = '1.1'
__all__ = ['open', 'mailto']

import os

_controllers = {}
_open = None


class BaseController(object):
    '''Base class for open program controllers.'''

    def __init__(self, name):
        self.name = name

    def open(self, filename):
        raise NotImplementedError


class Controller(BaseController):
    '''Controller for a generic open program.'''

    def __init__(self, *args):
        super(Controller, self).__init__(os.path.basename(args[0]))
        self.args = list(args)

    def _invoke(self, cmdline):
        closefds = False
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        inout = file(os.devnull, 'r+')

        # if possible, put the child precess in separate process group,
        # so keyboard interrupts don't affect child precess as well as
        # Python
        setsid = getattr(os, 'setsid', None)
        if not setsid:
            setsid = getattr(os, 'setpgrp', None)

        pipe = subprocess.Popen(cmdline, stdin=inout, stdout=inout,
                                stderr=inout, close_fds=closefds,
                                preexec_fn=setsid, startupinfo=startupinfo)

        # It is assumed that this kind of tools (gnome-open, kfmclient,
        # exo-open, xdg-open and open for OSX) immediately exit after lauching
        # the specific application
        returncode = pipe.wait()
        if hasattr(self, 'fixreturncode'):
            returncode = self.fixreturncode(returncode)
        return not returncode

    def open(self, filename):
        if isinstance(filename, basestring):
            cmdline = self.args + [filename]
        else:
            # assume it is a sequence
            cmdline = self.args + filename
        try:
            return self._invoke(cmdline)
        except OSError:
            return False



class Start(BaseController):
    '''Controller for the win32 start progam through os.startfile.'''

    def open(self, filename):
        try:
            os.startfile(filename)
        except WindowsError:
            # [Error 22] No application is associated with the specified
            # file for this operation: '<URL>'
            return False
        else:
            return True

_controllers['windows-default'] = Start('start')
_open = _controllers['windows-default'].open


def dopen(filename):
    '''Open a file or an URL in the registered default application.'''

    return _open(filename)

