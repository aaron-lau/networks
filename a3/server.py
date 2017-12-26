#!/usr/bin/env python

# CS456 Assignment #3
# Aaron Lau
# 20572242

from socket import *

import threading
from _thread import *

import sys, string, random, signal, os

clientConnectionDict = {}
# thread fuction
def listenToClient(clientSocket, addr):
    while True:
        # data received from client
        try:
            data = clientSocket.recv(1024)
            paddedCommand = '{:<9}'.format(data.decode("utf-8"))
            if paddedCommand[0] == 'F':
                if paddedCommand == 'F        ':
                    # print ("Waiting for ongoing file exchanges")
                    while True:
                        exchanging = True
                        if not clientConnectionDict:
                            break
                        for key in clientConnectionDict:
                            exchanging = exchanging and clientConnectionDict[key][2]
                        if not exchanging:
                            for key in clientConnectionDict:
                                downloaderSocket = clientConnectionDict[key][0]
                                downloaderSocket.send("c!l!o!s!e".encode())
                                downloaderSocket.close()
                            break
                    # print ("Terminating server")
                    os._exit(1)
            elif paddedCommand[0] == 'G':
                key = paddedCommand[1:]
                # print ("client at {} wants to DOWNLOAD using key {}".format(addr,key))
                # assumption is that downloader connects to server first thus
                # save the downloader socket in a dict where the command key is the dictionary key
                clientConnectionDict[key] = [clientSocket, addr, False]
            elif paddedCommand[0] == 'P':
                key = paddedCommand[1:]
                # print ("client at {} wants to UPLOAD using key {}".format(addr,key))
                if key in clientConnectionDict:
                    if clientConnectionDict[key][1] != addr:
                        # uploaded is ready to upload to another client
                        clientConnectionDict[key][2] = True
                        clientSocket.send("1".encode()) # send to uploader to begin uploading
                        downloaderSocket = clientConnectionDict[key][0]
                        # In case of download, the server responds with the binary data stream of the file.
                        while True:
                            data = clientSocket.recv(4096)
                            if not data:
                                downloaderSocket.send("c!l!o!s!e".encode())
                                downloaderSocket.close()
                                break
                            # print ("sending")
                            downloaderSocket.send(data)
                        del clientConnectionDict[key]
        except OSError as e:
            pass
    # connection closed
    clientSocket.close()

def main():
    serverSocket = socket(AF_INET,SOCK_STREAM)
    serverSocket.bind(('',0))
    # serverSocket.setblocking(0)
    serverSocket.listen(100)
    serverPort = serverSocket.getsockname()[1]
    print (serverPort)

    serverFile = open("port","w+")
    serverFile.write(str(serverPort) + '\n')
    serverFile.close()

    connectionsTable = {}
    while True:
        # establish connection with client
        connectionSocket, addr = serverSocket.accept()
        # start a new thread for the client
        threading.Thread(target = listenToClient,args = (connectionSocket,addr)).start()
    serverSocket.close()

if __name__ == '__main__':
	main()
