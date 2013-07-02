"""
# Copyright (C) 2007 Nathan Ramella (nar@remix.net)
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# For questions regarding this module contact
# Nathan Ramella <nar@remix.net> or visit http://www.liveapi.org

RemixNet Module

This module contains an OSC interface class to facilitate remote
control of Ableton Live through the OSC protocol.

Based on the original RemixNet.py written by Nathan Ramella (nar@remix.net)

-Updated 29/04/09 by ST8 (st8@q3f.org)
    Works on Mac OSX with Live7/8
    
    The socket module is missing on osx and including it from the
    default python install doesnt work.  Turns out its the os module
    that causes all the problems, removing dependance on this module
    and packaging the script with a modified version of the socket
    module allows it to run on osx.

-Updated May/June 2011 by Hans Huebner (hans.huebner@gmail.com)

    Refactored and removed methods that are not used.
    
    The original version of RemixNet.py had several classes to
    implement sending and receiving OSC packets.  This was relatively
    hard to change or update, and as I wanted to be able to change the
    destination of OSC packets sent out by live at run time, I decided
    to simplify RemixNet so that it only supports those functions that
    are actually used by LiveOSC.  In particular, OSCServer,
    OSCClient, UDPServer and UDPClient have all been collapsed into
    one class, OSCEndpoint.  OSCEndpoint uses one UDP socket to send
    and receive data.  By default, the socket is bound to port 9000 as
    before, but it listens to all network interfaces so that packets
    coming in from the network are accepted.  Also by default,
    outgoing packets are sent to localhost port 9001.  This can be
    changed by sending a /remix/set_peer message with two arguments,
    the host and the port number of the peer.  The host may optionally
    be sent as empty string.  In that case, the peer host will be
    automatically be set to the host that sent the /remix/set_peer
    message, making it easier to configure the OSC association.

    Also, the logging mechanism has been simplified.  It can now be
    used simply by importing the log function from the Logger module
    and then calling log() with a string argument.
"""
import sys
import errno
import Live
from Logger import log

# Import correct paths for os / version
version = Live.Application.get_application().get_major_version()
if sys.platform == "win32":
    import socket   

else:
    if version > 7:
       # 10.5
        try:
            file = open("/usr/lib/python2.5/string.pyc")
        except IOError:
            sys.path.append("/Library/Frameworks/Python.framework/Versions/2.5/lib/python2.5")
            import socket_live8 as socket  
        else:
            sys.path.append("/usr/lib/python2.5")
            import socket

import OSC 
            
class OSCEndpoint:
        
    def __init__(self, remoteHost='127.0.0.1', remotePort=9031, localHost='127.0.0.1', localPort=9030, ):
        """
      
        This is the main class we the use as a nexus point in this module.

        - remoteHost and remotePort define the address of the peer
          that we send data to by default.  It can be changed, at run
          time, using the /remix/set_peer OSC message.

        - localHost and localPort define the address that we are
          listening to for incoming OSC packets.  By default, we are
          listening on all interfaces with port 9000.
        
        By default we define and set callbacks for some utility
        addresses:
        
        /remix/echo - Echos back the string argument to the peer.
        /remix/time - Returns time.time() (time in float seconds)
        /remix/set_peer - Reconfigures the peer address which we send OSC messages to
        """

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setblocking(0)
        self.localAddr = (localHost, localPort)
        self.socket.bind(self.localAddr)

        self.remoteAddr = (remoteHost, remotePort)

        log('OSCEndpoint starting, local address ' + str(self.localAddr) + ' remote address ' + str(self.remoteAddr))
        
        # Create our callback manager and register some utility
        # callbacks
        
        self.callbackManager = OSC.CallbackManager()
        self.callbackManager.add('/remix/echo', self.callbackEcho)
        self.callbackManager.add('/remix/time', self.callbackEcho)
        self.callbackManager.add('/remix/set_peer', self.setPeer)
 
    def send(self, address, msg):
       
        """
        Given an OSC address and OSC msg payload we construct our
        OSC packet and send it to its destination. You can pass in lists
        or tuples in msg and we will iterate over them and append each 
        to the end of a single OSC packet.
        
        This can be useful for transparently dealing with methods that
        yield a variety of values in a list/tuple without the necessity of
        combing through it yourself.
        """
        
        oscMessage = OSC.OSCMessage(address, msg)
        self.sendMessage(oscMessage)

    def sendMessage(self, message):
        self.socket.sendto(message.getBinary(), self.remoteAddr)

    def processIncomingUDP(self):
        """
        This is the function that deals with incoming UDP messages.
        It processes messages as long as any are buffered in the
        socket, then returns.
        
        There are several limitations to the Ableton Live Python environment. 
        
        * The Ableton Live Python environment is minimal. The included module
          list is very short. For instance, we don't have 'select()'.
          
        * The Ableton Live Python version is a bit older than what most Python
          programmers are used to. Its version string says 2.2.1, and the Python
          webpage shows that the offical 2.2.3 came out May 30, 2003. So we've
          got 4 years between us and it. Fortunately since I didn't know any Python
          when I got started on this project the version differences didn't bother 
          me. But I know the lack of modern features has been a pain for a few
          of our developers.
          
        * The Ableton Live Python environment, although it includes the thread
          module, doesn't function how you'd expect it to. The threads appear to
          be on a 100ms timer that cannot be altered consistently through Python.
          
          I did find an interesting behavior in that when you modify the
          sys.setcheckinterval value to very large numbers for about 1-5/100ths of
          a second thread focus goes away entirely and if your running thread is
          a 'while 1:' loop with no sleep, it gets 4-5 iterations in before 
          the thread management stuff kicks in and puts you down back to 100ms 
          loop.
          
          As a goof I tried making a thread that was a 'while 1:' loop with a
          sys.setcheckinterval(50000) inside it -- first iteration it triggered
          the behavior, then it stopped.
          
          It should also be noted that you can make a blocking TCP socket using
          the threads interface. But your refresh is going to be about 40ms slower
          than using a non-blocking UDP socket reader. But hey, you're the boss!
          
          So far the best performance for processing incoming packets can be found
          by attaching a method as a listener to the Song.current_song_time 
          attribute. This attribute updates every 60ms on the dot allowing for 
          16 passes on the incoming UDP traffic every second.
          
          My machine is pretty beefy but I was able to sustain an average of
          over 1300 /remix/echo callback hits a second and only lost .006% 
          of my UDP traffic over 10 million packets on a machine running Live.
          
          One final note -- I make no promises as to the latency of triggers received.
          I haven't tested that at all yet. Since the window is 60ms, don't get 
          your hopes up about MIDI over OSC.
        """
        try:
            # Our socket is in non-blocking mode.  recvfrom will
            # either return the next packet waiting or raise an EAGAIN
            # exception that we catch to exit the reception loop.
            while 1:
                self.data, self.addr = self.socket.recvfrom(65536)
#                log('received packet from ' + str(self.addr))
                try:
                    self.callbackManager.handle(self.data, self.addr)
                except:
                    self.send('/remix/error', (str(sys.exc_info())))

        except Exception, e:
            err, message=e
            if err != errno.EAGAIN:                                 # no data on socket
                log('error handling message, errno ' + str(errno) + ': ' + message)

    def shutdown(self):
        """
        Close our socket.
        """
        self.socket.close()

    # standard callback handlers (in the /remix/ address name space)

    def setPeer(self, msg, source):
        """
        Reconfigure the client side to the address and port indicated
        as the argument.  The first argument is a string with the host
        address or an empty string if the IP address of the sender of
        the reconfiguration message should be used as peer.  The
        second argument is the integer port number of the peer.
        """
        host = msg[2]
        if host == '':
            host = source[0]
        port = msg[3]
        log('reconfigure to send to ' + host + ':' + str(port))
        self.remoteAddr = (host, port)
  
    def callbackEcho(self, msg, source):
        """
        When re receive a '/remix/echo' OSC query from another host
        we respond in kind by passing back the message they sent to us.
        Useful for verifying functionality.
        """
        
        self.send('/remix/echo', msg[2])
        
    def callbackTime(self, msg, source):
        """
        When we receive a '/remix/time' OSC query from another host
        we respond with the current value of time.time()
        
        This callback can be useful for testing timing/queue processing
        between hosts
        """

        self.send('/remix/time', time.time())
        
