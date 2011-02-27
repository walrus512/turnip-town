# -*- coding: utf-8 -*-
"""
GrooveWalrus: Http Server
Copyright (C) 2019
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
import BaseHTTPServer
import sys
from threading import Thread
from main_utils import pyro_server

PORT=8723

class ServerThread(Thread): 
    """ Loads a http server """
    def __init__(self):
        Thread.__init__(self)
        self.stopper = False

    def run(self):
        server_class=BaseHTTPServer.HTTPServer
        handler_class=HandyTheHandler
        server_address = ('', PORT)
        httpd = server_class(server_address, handler_class)
        httpd.serve_forever()        
        
class HandyTheHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
        
    def do_GET(s):
        """Respond to a GET request."""
        if s.path == '/refresh':
            s.send_response(200)
            s.send_header("Content-type", "text/html")
            s.end_headers()
            stdout = sys.stdout
            sys.stdout = s.wfile        
            DoStuff(s.path)
            sys.stdout = stdout
        else:            
            s.send_response(200)
            s.send_header("Content-type", "text/html")
            s.end_headers()
            s.wfile.write(HTML_TOP)
            s.wfile.write("<span class=\"action\">Last Action: %s</span>" % s.path)
            s.wfile.write(HTML_B1)
            stdout = sys.stdout
            sys.stdout = s.wfile        
            DoStuff(s.path)
            sys.stdout = stdout
            s.wfile.write(HTML_BOTTOM)
            
    def log_request(self, code=None, size=None):
        pass
        #print('Request')

    def log_message(self, format, *args):
        #print('Message')
        pass

         
def DoStuff(path):
    play_func = ['play', 'stop', 'pause', 'next', 'previous', 'mute', 'volume_up', 'volume_down', 'refresh', 'random', 'repeat']
    p_set = set(play_func)
    if path[1:] in p_set:
        #print path[1:]
        pyro_server.SendPlaybackPyro(path[1:])
    if path[1:].isdigit():
        pyro_server.SendPlaybackPyro(path[1:])
        #print path[1:]
    
class HttpControl():
    def __init__(self):
        self.current = ServerThread()
        
    def StartHttp(self):
        self.current.start()
        
    def StopHttp(self):    
        pass
        
        
        
        
HTML_TOP = """
<html>
    <head>
    <title>GrooveWalrus Web Remote</title></head>
    <style type="text/css">
    hr {color:sienna; width:220px;}
    p {}
    .refresh{text-align: left; font-size:.75em;}
    body {margin:20px; font-family:sans-serif; background-color:#476552;}
    .remote {padding:1px; margin:0px; border:3px solid #9de3b7; width:500px; background-color:#7c9481}
    .stats {padding:1px; margin:0px; border:3px solid #9de3b7; border-top:0px; width:500px; background-color:#c2eccb}
    .title {font-size:1.5em; padding:10px; line-height:0.9em;}
    .action {font-size:.75em;}
    pre {width:480px; Overflow:Hidden; Word-wrap:Break-word;}
    pre a {color:#000}
    .controls { overflow:hidden; width:500px;
    padding:1px; background-color:#83bc8f; border:3px solid #9de3b7; border-top:0px;}
    .controls a{ display:block; float:left; width:122px; height:45px; font-family:arial;
    font-size:11px; text-transform:uppercase; text-decoration:none; color:#444;
    line-height:45px; text-align:center; }
    .controls a:hover{background-color:#dcffe9;}
    .current{background-color:7c9481; color:#FFF;}
    .current a {color:#FFF;}    
    .controls2 { overflow:hidden; width:500px;
    padding:1px; background-color:#70d685; border:3px solid #9de3b7; border-top:0px;}
    .controls2 a{ display:block; float:left; width:98px; height:35px; font-family:arial;
    font-size:11px; text-transform:uppercase; text-decoration:none; color:#555;
    line-height:35px; text-align:center; }
    .controls2 a:hover{background-color:#eefff4;}                    
    </style>
    <script type="text/javascript">
    var page = "/refresh";
    function ajax(url,target)
     {
        // native XMLHttpRequest object
       // document.getElementById(target).innerHTML = 'sending...';
       if (window.XMLHttpRequest) {
           req = new XMLHttpRequest();
           req.onreadystatechange = function() {ajaxDone(target);};
           req.open("GET", url, true);
           req.send(null);
       // IE/Windows ActiveX version
       } else if (window.ActiveXObject) {
           req = new ActiveXObject("Microsoft.XMLHTTP");
           if (req) {
               req.onreadystatechange = function() {ajaxDone(target);};
               req.open("GET", url, true);
               req.send();
           }
       }
    		   setTimeout("ajax(page,'scriptoutput')", 5000);
    }
    
        function ajaxDone(target) {
            // only if req is "loaded"
            if (req.readyState == 4) {
            // only if "OK"
                if (req.status == 200 || req.status == 304) {
                    results = req.responseText;
                    document.getElementById(target).innerHTML = results;
                } else {
                    document.getElementById(target).innerHTML="ajax error:" + req.statusText;
                }
            }
        }
    </script>
    </head>
    <body onload="ajax(page,'scriptoutput')">
    <div class="remote">                
        <p>                    
        <span class="title">GrooveWalrus Remote</span>
"""

HTML_B1 = """
        </p>
    </div>
    <div class="controls2">       
        <a href="/mute">mute</a>
        <a href="/volume_up">volume up</a>
        <a href="/volume_down">volume down</a>
        <a href="/random">random</a>
        <a href="/repeat">repeat</a>
    </div>
    <div class="controls">       
        <a href="/previous">previous</a>
        <a href="/play">play / pause</a>
        <a href="/stop">stop</a>
        <a href="/next">next</a>
    </div>
    <div class="stats"><pre id="scriptoutput">
"""

HTML_BOTTOM = """
    </pre></div>
    </body>
</html>
"""
        
        
        
        
        
        
        
        
        
        
        

if __name__ == '__main__':
    HttpControl().StartHttp()