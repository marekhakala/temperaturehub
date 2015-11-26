#!/usr/bin/python

import sys
import os
import time
import BaseHTTPServer

sys.path.append(os.path.abspath("./"))
from xml_loader import *

HOSTNAME = '127.0.0.1'
TCP_PORT = 9000

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/xml")
        s.end_headers()

    def do_GET(s):
        s.send_response(200)
        s.send_header("Content-type", "text/xml")
        s.end_headers()

        if s.path == "/schema.xsd":
            loader = XMLLoader("./schema.xsd")
        else:
            loader = XMLLoader("./client.xml")

        loader.loadFile()
        content = loader.getContent()
        s.wfile.write(str(content))

if __name__ == '__main__':
    http_server = BaseHTTPServer.HTTPServer
    httpd = BaseHTTPServer.HTTPServer((HOSTNAME, TCP_PORT), MyHandler)
    print time.asctime() + " Temperature SRV Starts -> " + str(HOSTNAME) + ":" + str(TCP_PORT)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

    httpd.server_close()
    print time.asctime() + " Temperature SRV Stops -> " + str(HOST) + ":" + str(TCP_PORT)
