#!/usr/bin/env python

# CS456 Assignment #1
# Aaron Lau
# 20572242

from socket import *
import sys, string

# initiate(server_address, n_port, req_code):
# Uses a UDP connection to contact the server at server_address and n_port and sends the req_code
# The method recvfrom also takes the buffer size 2048 as input. (This buffer size works for most purposes.)
# Returns: r_port
def initiate(server_address, n_port, req_code):
	# print ("initiate")
	try:
		clientUDPSocket = socket(AF_INET, SOCK_DGRAM)
	except error, e:
		print ("Invalid negotiation port")

	clientUDPSocket.sendto(str(req_code), (server_address, n_port))
	r_port, serverAddress = clientUDPSocket.recvfrom(2048)
	clientUDPSocket.close()
	return r_port

# confirmation(server_address, n_port, req_code):
# Uses a UDP connection to contact the server at server_address and n_port and confirms the the r_port is correct
# If the confirmMessage is as expected than the program will continue, else program will quit
# The method recvfrom also takes the buffer size 2048 as input. (This buffer size works for most purposes.)
def confirmation(server_address, n_port, r_port):
	# print ("confirmation")
	clientUDPSocket = socket(AF_INET, SOCK_DGRAM)
	clientUDPSocket.sendto(str(r_port), (server_address, n_port))
	confirmMessage, serverAddress = clientUDPSocket.recvfrom(2048)
	clientUDPSocket.close()
	if confirmMessage == 'ok':
		return
	print ("Server could not confirm r_port")

# sendMessage(server_address, r_port, msg):
# Uses a TCP connection to contact the server at server_address and n_port and sends msg
# The reverse message should be returned from the server and this is what is returned
# Returns: reversedMessage
def sendMessage(server_address, r_port, msg):
	# print ("sendMessage")
	TCPSocket = socket(AF_INET, SOCK_STREAM)
	TCPSocket.connect((server_address, int(r_port)))		
	TCPSocket.send(msg)			
	reversedMessage = TCPSocket.recv(2048)
	TCPSocket.close()
	return reversedMessage

# main():
# main logic that parses arguments and coordinates entire client communication
def main():
	server_address = sys.argv[1]
	n_port = int(sys.argv[2])
	req_code = int(sys.argv[3])
	msg = sys.argv[4]

	r_port = initiate(server_address, n_port, req_code)	#Client sends a request code through the UDP socket
	confirmation(server_address, n_port, r_port)
	reversedMessage = sendMessage(server_address, r_port, msg)	#Complete the transaction using UDP, receive the reversed message
	print reversedMessage

main()
