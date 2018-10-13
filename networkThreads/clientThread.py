#! /usr/bin/env python3

# Echo client program
import socket, sys, re, os
import params
from framedSock import FramedStreamSock
from threading import Thread
import time

port = input("would you like to use the stammer proxy? (y/n)\n")
if 'y' in port:
    port = "50000"
else:
    port = "50001"

switchesVarDefaults = (
    (('-s', '--server'), 'server', "localhost:" + port),
(('-d', '--debug'), "debug", False), # boolean (set if present)
(('-?', '--usage'), "usage", False), # boolean (set if present)
)


progname = "ClientThread"
paramMap = params.parseParams(switchesVarDefaults)

server, usage, debug  = paramMap["server"], paramMap["usage"], paramMap["debug"]

if usage:
    params.usage()

try:
    serverHost, serverPort = re.split(":", server)
    serverPort = int(serverPort)
except:
    print("Can't parse server:port from '%s'" % server)
    sys.exit(1)

class ClientThread(Thread):
    def __init__(self, serverHost, serverPort, debug):
        Thread.__init__(self, daemon=False)
        self.serverHost, self.serverPort, self.debug = serverHost, serverPort, debug
        self.start()
    def run(self):
        s = None
        for res in socket.getaddrinfo(serverHost, serverPort, socket.AF_UNSPEC, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            try:
                print("creating sock: af=%d, type=%d, proto=%d" % (af, socktype, proto))
                s = socket.socket(af, socktype, proto)
            except socket.error as msg:
                print(" error: %s" % msg)
                s = None
                continue
            try:
                print(" attempting to connect to %s" % repr(sa))
                s.connect(sa)
            except socket.error as msg:
                print(" error: %s" % msg)
                s.close()
                s = None
                continue
            break

        if s is None:
            print('could not open socket')
            sys.exit(1)

        fs = FramedStreamSock(s, debug=debug)

        files = os.listdir(os.curdir)  #grab current files
        print(files)
        inputFile = input("Please select a file to send \n")
        #Attemps to read input as file
        try:
            with open(inputFile.strip(),"rb") as binary_file:
                # Read the whole file at once
                data = binary_file.read()
        except FileNotFoundError:
            print("file not found exiting")
            sys.exit(0)
        try:
            #sends file information to server
            fs.sendmsg(inputFile.strip().encode('utf-8') + b"\'start\'")
        except BrokenPipeError:
            print("disconnected start again")
            sys.exit(0)
        #send 100 bits at a time
        while len(data) >= 100:
            line = data[:100]
            data = data[100:]
            try:
                fs.sendmsg(line)
                print("received:", fs.receivemsg())
            except BrokenPipeError:
                print("disconnected start again")
                sys.exit(0)
        #sends left over bits
        if len(data) > 0:
            fs.sendmsg(data)
            print("received:", fs.receivemsg())
        try:
        #tells server file has ended
            fs.sendmsg(b"\'end\'")
            print("received:", fs.receivemsg())
        except BrokenPipeError:
            print("disconnected start again")
            sys.exit(0)


ClientThread(serverHost, serverPort, debug)

