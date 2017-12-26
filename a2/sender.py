#!/usr/bin/env python

# CS456 Assignment #2
# Aaron Lau
# 20572242

from socket import *
from struct import *
import sys, string, time, math, threading, signal

sendBaseSeqNum = 0
eotReceived = False
sendBuffer = []
timeouts = []
windowSize = 10
lock = threading.Lock()
firstInWindow = 0
lastInWindow = firstInWindow + windowSize -1
eotAckReceived = False

## Keep track of the timeout values which are sent to the server
def timeoutHandler(signum, frame):
    global protocol
    global timeouts
    global windowSize
    global sendBuffer
    global lock
    global senderSocket
    global channelIP
    global channelPort
    global sendBaseSeqNum
    global firstInWindow
    global lastInWindow
    global timeout

    # Protocol = Go back N
    if protocol == 0:
        for index, timeoutValue in enumerate(timeouts):
            timeouts[index] = timeoutValue - 1
        if len(timeouts) > 0 and timeouts[0] <= 0:
            lock.acquire()
            while True:
                try:
                    print ("PKT SEND DAT {} {}".format(sendBuffer[0][0]+12, sendBuffer[0][1]))
                    resendPacket = sendBuffer[0][2]
                    senderSocket.sendto(resendPacket,(channelIP.decode("utf-8") , int(channelPort.decode("utf-8")) ))
                    timeouts[0] = timeout
                    break
                except:
                    pass
            lock.release()
    elif protocol == 1:
        for i in range(windowSize):
            counter = firstInWindow + i
            counter %= 256
            timeouts[counter % windowSize] = timeouts[counter % windowSize] - 1
            lock.acquire()
            if timeouts[counter % windowSize] <= 0 and sendBuffer[counter % windowSize] != None:
                while True:
                    if sendBuffer[counter % windowSize] != None:
                        # this try/catch is necessary for when the I/O buffer is
                        try:
                            print ("PKT reSEND DAT {} {}".format(sendBuffer[counter % windowSize][0]+12, sendBuffer[counter % windowSize][1]))
                            resendPacket = sendBuffer[counter % windowSize][2]
                            senderSocket.sendto(resendPacket,(channelIP.decode("utf-8") , int(channelPort.decode("utf-8")) ))
                            timeouts[counter % windowSize] = timeout
                            break
                        except:
                            pass
                    else:
                        break
            lock.release()


# function that will run in another thread to wait for ACKS
def getACKs(senderSocket, throwaway):
    global protocol
    global timeouts
    global windowSize
    global sendBuffer
    global lock
    global sendBaseSeqNum
    global firstInWindow
    global lastInWindow
    global eotAckReceived

    while True:
        ackPacket, addr = senderSocket.recvfrom(4096)
        packet = unpack('!III', ackPacket)
        packetType = packet[0]
        packetLength = packet[1]
        ackNum = packet[2]
        print ("PKT RECV ACK {} {}".format(packetLength, ackNum))
        # Protocol = Go back N
        if protocol == 0:
            if packetType == 1:
                if ackNum == sendBaseSeqNum:
                    lock.acquire()
                    sendBuffer.pop(0)
                    timeouts.pop(0)
                    sendBaseSeqNum+=1
                    sendBaseSeqNum%=256
                    lock.release()
            elif packetType == 2:
                print ("PKT RECV EOT {} {}".format(packetLength, ackNum))
                signal.setitimer(signal.ITIMER_REAL, 0, 0)
                exit()
        elif protocol == 1:
            if packetType == 1:
                if ackNum == firstInWindow:
                    lock.acquire()
                    for i in range(firstInWindow, lastInWindow + 1):
                        sendBuffer[i % windowSize] = None
                        timeouts[i % windowSize] = 0
                        firstInWindow+=1
                        firstInWindow%=256
                        lastInWindow+=1
                        lastInWindow%=256
                        if sendBuffer[(i + 1)% windowSize] != None:
                            break
                    lock.release()
                elif ackNum >= firstInWindow and ackNum <= lastInWindow:
                    sendBuffer[ackNum % windowSize] = None
                    timeouts[ackNum % windowSize] = 0
            elif packetType == 2:
                print ("PKT RECV EOT {} {}".format(packetLength, ackNum))
                signal.setitimer(signal.ITIMER_REAL, 0, 0)
                eotAckReceived = True
                exit()

def main():
    global sendBaseSeqNum
    global protocol
    global senderSocket
    global channelIP
    global channelPort
    global timeout
    global firstInWindow
    global lastInWindow
    global eotAckReceived
    # Receiver <protocol selector> <filename>
    protocol = int(sys.argv[1])
    timeout = int(sys.argv[2])   # timeout in milliseconds
    filename = sys.argv[3]
    senderIP = "127.0.0.1"
    windowSize = 10

    senderSocket = socket(AF_INET, SOCK_DGRAM)
    senderSocket.bind((senderIP, 0))

    if protocol == 1:
        for i in range(windowSize):
            sendBuffer.append(None)
            timeouts.append(0)

    data = []
    # read channelInfo
    with open('channelInfo', 'rb') as f:
        channelInfo = f.read()
        channelIP, channelPort = channelInfo.split()

    print (channelIP.decode("utf-8") , int(channelPort.decode("utf-8")))
    # read input data
    with open(filename, 'rb') as f:
        while 1:
            datachunk = f.read(500)
            if not datachunk:
                break
            data.append(datachunk)

    # Start thread looking for acknowledgements
    threadForAck = threading.Thread(name="ACKsThread", target=getACKs, args=(senderSocket, 0))
    threadForAck.daemon = True
    threadForAck.start()

    signal.signal(signal.SIGALRM, timeoutHandler)
    signal.setitimer(signal.ITIMER_REAL, 0.001, timeout*0.001)

    seqNum = 0
    while data != []:
        if protocol == 0:
            if len(sendBuffer) < windowSize:
                datachunk = data.pop(0)
                packet = pack('!III'+ str(len(datachunk)) +'s', 0,len(datachunk)+12,seqNum,datachunk)
                print ("PKT SEND DAT " + str(12 + len(datachunk)) + " {} ".format(seqNum))
                senderSocket.sendto(packet,(channelIP.decode("utf-8") , int(channelPort.decode("utf-8")) ))
                sendBuffer.append((len(datachunk),seqNum,packet))
                timeouts.append(timeout)
                seqNum += 1
                seqNum %= 256
        elif protocol == 1:
            if seqNum <= lastInWindow:
                datachunk = data.pop(0)
                packet = pack('!III'+ str(len(datachunk)) +'s', 0,len(datachunk)+12,seqNum,datachunk)
                print ("PKT SEND DAT " + str(12 + len(datachunk)) + " {} ".format(seqNum))
                senderSocket.sendto(packet,(channelIP.decode("utf-8") , int(channelPort.decode("utf-8")) ))
                sendBuffer[seqNum % windowSize] = (len(datachunk),seqNum,packet)
                timeouts[seqNum % windowSize] = timeout
                seqNum += 1
                seqNum %= 256

    if protocol == 0:
        while sendBuffer != []:
            pass
    elif protocol == 1:
        while True:
            if all(value is None for value in sendBuffer):
                break

    eotPacket = pack('!III', 2, 12, 0)
    print ("PKT SEND EOT 12 0")
    senderSocket.sendto(eotPacket,(channelIP.decode("utf-8") , int(channelPort.decode("utf-8")) ))

    while not eotAckReceived:
        pass


if __name__ == '__main__':
	main()
