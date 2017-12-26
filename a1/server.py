#!/usr/bin/env python

# CS456 Assignment #1
# Aaron Lau
# 20572242

from socket import *
import sys, string, random, signal
runtime = 60				#Server runtime before shutting down

# shutdown(throwaway1, throwaway2):
# shuts the server down when a signal is triggers. The parameters are not used.
def shutdown(throwaway1, throwaway2):
	print "Server shutting down"
	quit()
	
# udpInitiation (n_port, req_code):
# Establish a udp connection to clients who are trying to reach the server at the 
# given negotiation port and the request code
# Return: r_port
def udpInitiation (n_port, req_code):
	# print ("udpInitiation")
	listening = 1
	while listening:
		client_req_code, clientAddress = n_port.recvfrom(2048)
		if str(client_req_code) == str(req_code):
			r_port = socket(AF_INET, SOCK_STREAM)
			r_port.bind(('', 0))
			n_port.sendto(str(r_port.getsockname()[1]), clientAddress)
			listening = 0
		else:
			print ("Received incorrect request code")
	return r_port

# reqCodeConfirmation (r_port, n_port):
# Establish a udp connection to clients to confirm they have received the correct r_port
def reqCodeConfirmation (r_port, n_port):
	# print ("reqCodeConfirmation")
	listening = 1
	while listening:
		clientRPort, clientAddress = n_port.recvfrom(2048)
		if str(clientRPort) == str(r_port.getsockname()[1]):
			n_port.sendto('ok', clientAddress)
			listening = 0
		else:
			print ("Received incorrect r socket")

# reqCodeConfirmation (r_port, n_port):
# Establish a tcp connection to clients and receive a message in which that message will be reversed
# and sent back to the client
# Return: reversedMessage
def tcpMessageTransform(r_port):
	r_port.listen(1)
	listening = 1
	while listening:
		connectionSocket, addr = r_port.accept()
		message = connectionSocket.recv(1024)
		# Print the received message
		print ("SERVER_RCV_MSG=" + str(message))
		reversedMessage = message[::-1]
		connectionSocket.send(reversedMessage)	
		connectionSocket.close()
		listening = 0
	return reversedMessage

#Main
# main logic that parses arguments and coordinates entire server communication
def main():
	signal.signal(signal.SIGALRM, shutdown)				# Set the signal for shutdown
	signal.alarm(runtime) 								# server.py will quit after the runtime length has been reached
	req_code = sys.argv[1]
	n_port = socket(AF_INET, SOCK_DGRAM)
	n_port.bind(('', 0))						# choose a free port

	print ("SERVER_PORT=" + str(n_port.getsockname()[1]))	# print the n_port for the client to use
	
	while 1:
		r_port = udpInitiation(n_port, req_code)
		print ("SERVER_TCP_PORT=" + str(r_port.getsockname()[1]))	# print the r_port
		reqCodeConfirmation (r_port, n_port)
		reversedMessage = tcpMessageTransform(r_port)
		
main()
