import SimpleHTTPServer
import SocketServer
from thread import start_new_thread
import time
import glob
import urllib2
import re
import json
import weatherLib


class myHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    
    def end_headers(self):
        self.send_my_headers()
        SimpleHTTPServer.SimpleHTTPRequestHandler.end_headers(self)

    def send_my_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")

# uncomment to disable HTTP messages on console  
#    def log_message(self, format, *args):
#        pass
    
    def do_GET(self):
        path = self.path

#dbg
#        print path
        
        rsp = None

        if path.startswith( '/current' ):
            rsp = W.getCurrent()

        if path.startswith( '/forecasts_zone' ):
            rsp = W.forecasts_zone()

        if path.startswith( '/forecasts_week' ):
            rsp = W.forecasts_week()

        if rsp :
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps(rsp))
            return

       
        if path.startswith( '/STATUS' ):
            # live status here
            return
            
        return SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)


#### MAIN ####
def server() :
    HTTP_PORT = 8800

    ## web server
    SocketServer.TCPServer.allow_reuse_address=True
    httpd = SocketServer.TCPServer(("0.0.0.0", HTTP_PORT), myHandler)
     
    print "Web server at port", HTTP_PORT
    httpd.serve_forever()


W = weatherLib.weatherNOAA()
if 1 :
    server()
    exit(0)

