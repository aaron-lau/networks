#!/usr/bin/env python

# CS456 Assignment #2
# Aaron Lau
# 20572242

from socket import *
from struct import *
import sys, string, time, math

def main():
    # Receiver <protocol selector> <filename>
    protocolSelector = int(sys.argv[1])
    filename = sys.argv[2]
    receiverIP = "127.0.0.1"

    receiverSocket = socket(AF_INET, SOCK_DGRAM)
    receiverSocket.bind((receiverIP, 0))    # choose a free port

    recvInfo = open("recvInfo","w+")
    recvInfo.write(receiverIP + ' ' + str(receiverSocket.getsockname()[1]) + '\n')
    recvInfo.close()

    # emptys file
    open(filename, 'w').close()

    expectedSeq = 0
    firstPackReceived = False

    windowSize = 10
    firstInWindow = 0
    lastInWindow = firstInWindow + windowSize - 1
    receiveBuffer = []
    for i in range(windowSize):
        receiveBuffer.append(None)

    while True:
        message, senderAddress = receiverSocket.recvfrom(4096)
        packet = unpack('!III'+str(len(message) - 12)+'s', message)
        packetType = packet[0]
        packetLength = packet[1]
        seqNum = packet[2]
        payload = packet[3]
        # print received packet
        if packetType == 0:
            print ("PKT RECV DAT " + str(packetLength) + ' ' + str(seqNum))
        elif packetType == 2:
            print ("PKT RECV EOT " + str(packetLength) + ' ' + str(seqNum))
            print ("PKT SEND EOT 12 0")
            ackEOTPacket = pack('!III', 2, 12, 0)
            receiverSocket.sendto(ackEOTPacket, senderAddress)
            break
        # Go-Back-N
        if protocolSelector == 0:
            if seqNum == expectedSeq:
                # acknowledgement packet
                ackPacket = pack('!III', 1, 12, seqNum)
                receiverSocket.sendto(ackPacket, senderAddress)
                print ("PKT SEND ACK 12 {} ".format(seqNum))
                # write to file
                with open(filename, "a") as f:
                    f.write(str(payload,'utf-8'))
                # update expectedSeq
                expectedSeq += 1
                firstPackReceived = True
                if expectedSeq >= 256:
                    expectedSeq %= 256
            else:
                if firstPackReceived:
                    # send acknowledgement for last received packet
                    if (expectedSeq == 0):
                        ackPacket = pack('!III', 1, 12, 255)
                        receiverSocket.sendto(ackPacket, senderAddress)
                        print ("PKT SEND ACK 12 {} ".format(255))
                    else:
                        ackPacket = pack('!III', 1, 12, expectedSeq - 1)
                        receiverSocket.sendto(ackPacket, senderAddress)
                        print ("PKT SEND ACK 12 {} ".format(expectedSeq - 1))
        # # Selective Repeat
        elif protocolSelector == 1:
            if seqNum < firstInWindow:
                # received old packet
                print ("PKT SEND ACK 12 {} ".format(seqNum))
                ackPacket = pack('!III', 1, 12, seqNum)
                receiverSocket.sendto(ackPacket, senderAddress)
            elif seqNum >= firstInWindow and seqNum <= lastInWindow:
                if seqNum == firstInWindow:
                    receiveBuffer[firstInWindow % windowSize] = packet
                    for i in range(firstInWindow, lastInWindow + 1):
                        # print the buffered data into the file
                        with open(filename, "a") as f:
                            toWritePayload = receiveBuffer[i % windowSize][3]
                            f.write(str(toWritePayload,'utf-8'))
                        # advance the window to the next not-yet received pkt
                        receiveBuffer[i % windowSize] = None
                        firstInWindow += 1
                        lastInWindow += 1
                        firstInWindow %= 256
                        lastInWindow %= 256
                        if receiveBuffer[(i + 1) % windowSize] == None:
                            break
                else:
                    # buffer out of order packet
                    receiveBuffer[seqNum % windowSize] = packet
                print ("PKT SEND ACK 12 {} ".format(seqNum))
                ackPacket = pack('!III', 1, 12, seqNum)
                receiverSocket.sendto(ackPacket, senderAddress)
if __name__ == '__main__':
	main()
