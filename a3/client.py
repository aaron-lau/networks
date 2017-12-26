#!/usr/bin/env python

# CS456 Assignment #3
# Aaron Lau
# 20572242

from socket import *
import time
import sys, string, random, signal
from ast import literal_eval

def main():
    # Receiver <protocol selector> <filename>
    if len(sys.argv) < 4:
        print ("Too few parameters given: {}".format(sys.argv[0]))
        exit()
    elif len(sys.argv) > 7:
        print ("Too many parameters given: {}".format(sys.argv[0]))
        exit()

    with open('port', 'rb') as f:
        hostPort = int(f.read())

    host = sys.argv[1]
    port = sys.argv[2]
    command = sys.argv[3]
    clientSocket = socket(AF_INET,SOCK_STREAM)
    clientSocket.connect((host, int(port)))
    if len(sys.argv) == 4:
        # terminate server
        if command[0] != 'F':
            print ("Expected TERMINATE command. Given '{}' instead".format(command[0]))
        else:
            clientSocket.send(command.encode())
    elif len(sys.argv) == 6:
        # download
        key = command[1:]
        if command[0] != 'G':
            print ("Expected GET command. Given '{}' instead".format(command[0]))
        else:
            fileName = sys.argv[4]
            recvSize = sys.argv[5]
            outputFile = open(fileName, 'w')
            data = []
            clientSocket.send(command.encode())
            while clientSocket:
                dataChunk = clientSocket.recv(int(recvSize))
                if dataChunk.decode() == "c!l!o!s!e":
                    # downloading complete
                    break
                data.append(dataChunk.decode())
            for dataChunk in data:
                outputFile.write(dataChunk)
            outputFile.close()

    elif len(sys.argv) == 7:
        # upload
        key = command[1:]
        if command[0] != 'P':
            print ("Expected PUT command. Given '{}' instead".format(command[0]))
        else:
            fileName = sys.argv[4]
            sendSize = sys.argv[5]
            waitTime = sys.argv[6]  #Wait time in milliseconds. Assume wait time is always below 1 second
            data = []
            with open(fileName, 'rb') as f:
                # read file into data
                while 1:
                    datachunk = f.read(int(sendSize))
                    if not datachunk:
                        break
                    data.append(datachunk)
            clientSocket.send(command.encode())
            ack = clientSocket.recv(int(1024))
            # In case of an upload, the above 9-byte control information is immediately
            # followed by the binary data stream of the file.
            while True:
                if not data:
                    # uploading complete
                    break
                time.sleep (float(waitTime) / 1000.0)
                datachunk = data.pop(0)
                clientSocket.send(datachunk)
            # When a client has completed a file upload, it closes the connection.
            clientSocket.close()

    else:
        print ("Incorrect number of parameters given: {}".format(sys.argv[0]))
        exit()


if __name__ == '__main__':
	main()
