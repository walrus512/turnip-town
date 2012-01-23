# -*- coding: utf-8 -*-
# Marcelo Barros de Almeida
# marcelobarrosalmeida (at) gmail.com
#
import sys
try:
    # http://www.developer.nokia.com/Community/Discussion/showthread.php?163939-Selecting-access-point-in-1.9.2-with-socket-module&p=575213
    # Try to import 'btsocket' as 'socket' - ignored on versions < 1.9.x
    sys.modules['socket'] = __import__('btsocket')
except ImportError:
    pass
import socket
import urllib
from urllib import unquote, splittype, splithost
 
__all__ = [ "UrllibProxy" ]
 
class _FancyURLopener(urllib.FancyURLopener):
    """ This class handles basic auth, providing user and password
        when required by twitter
    """
    def __init__(self, usr, pwd, prx={}):
        """ Set default values for local proxy (if any)
            and set user/password for twitter
        """
        urllib.FancyURLopener.__init__(self,prx)
        self.usr = usr
        self.pwd = pwd
 
    def prompt_user_passwd(self, host, realm):
        """ Basic auth callback
        """
        return (self.usr,self.pwd)
 
class UrllibProxy(object):
    """ Simple class for fetching URLs via urllib.
        It adds proxy support and http basic authentication.
    """
    def __init__(self, proxy="", usr="", pwd=""):
        """ Access a given url using proxy and possible http basic auth.
            Arguments:
 
            proxy  : standard proxy string, like http://username:password@proxy_ip:proxy_port
                     For proxies without authentication, just use http://proxy_ip:proxy_port
            usr,pwd: if the site you want to access required basic HTTP authentication, like twitter,
                     provide user and password for this site. This authetication is not related to
                     the previous proxy authentication.
        """
        self.proxy = proxy
        self.url = ""
        self.usr, self.pwd = usr, pwd
        self.user_agent = "urllib/1.0 (urllib)"
        self._prepare_urlopener()
 
    def _prepare_urlopener(self):
        """ Update twitter status
            Inspired in http://code.activestate.com/recipes/523016/
        """
        if self.proxy:
            XXX, r_type = splittype(self.proxy)
            phost, XXX = splithost(r_type)
            puser_pass = None
            if '@' in phost:
                user_pass, phost = phost.split('@', 1)
                if ':' in user_pass:
                    user, password = user_pass.split(':', 1)
                    puser_pass = ('%s:%s' %
                                  (unquote(user),
                                  unquote(password))).encode('base64').strip()            
            self.urlopener_proxy = {'http':'http://%s'%phost}
            if not puser_pass:
                self.headers = [('User-agent', self.user_agent)]
            else:
                self.headers = [('User-agent', self.user_agent),
                                ('Proxy-authorization', 'Basic ' + puser_pass) ]
        else:
            self.urlopener_proxy = {}
            self.headers = []
 
    def urlopener(self):
        """ Return an urlopener with authentication headers and proxy already set
        """
        urlopener = _FancyURLopener(self.usr, self.pwd, self.urlopener_proxy)
        urlopener.addheaders = self.headers
        return urlopener
 
    def open(self,url,params=""):
        self.url = url
        if params:
            f = self.urlopener().open(self.url,params) #post
        else:
            f = self.urlopener().open(self.url) #get
 
        return f
 
    def urlretrieve(self, url, filename=None):
        if not filename:
            filename = url[url.rfind("/") + 1:]
        f = open(filename,"wb")    
        f.write(self.open(url).read())
 
 
if __name__ == "__main__":
 
    local_file = "e:\\Wordmobi-0.7.0.zip"
    url = "http://wordmobi.googlecode.com/files/Wordmobi-0.7.0.zip"
    proxy = "http://username:password@192.168.1.40:8080"
 
    urlprx = UrllibProxy(proxy)
    urlprx.urlretrieve(url, local_file)