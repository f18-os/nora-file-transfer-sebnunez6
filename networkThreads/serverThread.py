#! /usr/bin/env python3
import sys, os, socket, params, time
from threading import Thread
import threading
from framedSock import FramedStreamSock
if not  os.path.isdir("Server"):
    os.makedirs("Server")
switchesVarDefaults = (
    (('-l', '--listenPort') ,'listenPort', 50001),
(('-d', '--debug'), "debug", False), # boolean (set if present)
(('-?', '--usage'), "usage", False), # boolean (set if present)
)

progname = "ServerThread"
paramMap = params.parseParams(switchesVarDefaults)

debug, listenPort = paramMap['debug'], paramMap['listenPort']

if paramMap['usage']:
    params.usage()

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # listener socket
bindAddr = ("127.0.0.1", listenPort)
lsock.bind(bindAddr)
lsock.listen(5)
print("listening on:", bindAddr)

class ServerThread(Thread):
    requestCount = 0            # one instance / class
    def __init__(self, sock, debug):
        Thread.__init__(self, daemon=True)
        self.fsock, self.debug = FramedStreamSock(sock, debug), debug
        self.start()
    def run(self):
        if not "Server" in os.getcwd():
            os.chdir("Server")
        start = self.fsock.receivemsg()
        try:
            start = start.decode()
        except AttributeError:
            print("error exiting: ", start)
            return

        count = 0
        for char in start:
                    if char.isalpha():
                        break
                    else:
                        count = count + 1
        start = start[count:]


        #tells server where file name ends
        start = start.split("\'start\'")

        #opening file
        file = open((start[0] ).strip(),"wb+")
        #lock the server
        requestNum = ServerThread.requestCount
        ServerThread.requestCount = requestNum + 1
        if lock:
            lock.acquire(True)
            print("Thread is now locked for input", requestNum)

        #Receives input while file has not ended
        while True:
            #error handling
            try:
                payload = self.fsock.receivemsg()
            except:
                pass

            #checking for debugging
            if debug: print("rec'd: ", payload)
            if not payload:
                break
            #checking if end of file else writes to file
            if b"\'end\'" in payload:
                lock.release()
                print("releasing lock for other threads")
                file.close()
                return
            else:
                file.write(payload)


while True:
    sock, addr = lsock.accept()
    #creating lock object
    lock = threading.Lock()
    ServerThread(sock, debug)
