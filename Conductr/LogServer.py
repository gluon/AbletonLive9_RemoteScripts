#!/usr/bin/env python

import SocketServer
import time
import sys

class LoggerRequestHandler(SocketServer.BaseRequestHandler):
    def setup(self):
        print self.client_address, 'connected!'

    def handle(self):
        while 1:
            time.sleep(0.01)
            data = self.request.recv(1024)
            if len(data) > 0:
                sys.stdout.write(data)

    def finish(self):
        print self.client_address, 'disconnected!'

if __name__=='__main__':
    SocketServer.ThreadingTCPServer.allow_reuse_address = True
    server = SocketServer.ThreadingTCPServer(('', 4444), LoggerRequestHandler)
    server.serve_forever()

