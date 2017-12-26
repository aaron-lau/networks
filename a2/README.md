To run the sender script use: ./Sender <protocol selector> <timeout> <filename>
To run the receiver script use: ./Receiver <protocol selector> <filename>

Tested on student linux enviroment:
- ubuntu1604-002

Python version: Python 3.6.3

All parts of the assignment have been completed:
  - Go N Back sender and receiver implemented
  - Selective Repeat sender and receiver implemented
  - NOTE: My code seems to hang unexpectedly when the sender timeout < 10

Sender.py
  The sender code is involves two threads, one (main) thread for initially
  sending out the data packets, and another thread for listening for ACKs
  from the Channel. There is also a timer for each packet in the window that
   is fired off depending on an interval define by the user. When the timer is
  fired off we determine if any packets have exceeded their TTL and if so they
  will be resent.

  The Go Back N is implemented using a queue data structure. The application
  always expects to receive an ACK for the packet at the front of the queue.

  The Selective Repeat is implemented using a list that mocks the window. The
  code keeps track of the firstInWindow and the firstInWindow + windowSize (lastInWindow)
  locations and expects ACKs [firstInWindow,lastInWindow]. If the ACK packet
  corresponds to the firstInWindow packet then we advance the window base to
  the next unACKed seqNum

Receiver.py
  The receiver code is constantly listening for data packets in a while loop.
  When it receives a packet from Sender, it will acknowledgement it and send a
  corresponding ACK packet.

  The Go Back N will return of expectedSeq - 1 if the packet is not the expectedSeq.

  The Selective Repeat has a receiverBuffer which will send buffer out of order
  packets. When a in order packet is received the program will print the buffered
  data into the file and advance the window to the next not-yet received pkt
