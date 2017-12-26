To run the server script use: ./server
To run the client script use: ./client <host> <port> <op-string> <file name> <send|recv size> <wait time>

Tested on student linux enviroment:
- ubuntu1604-002
- ubuntu1604-006
- ubuntu1604-008

Python version: Python 3.6.3

All parts of the assignment have been completed

server.py
  The server code will start off my listening for clients. The code can connect up to
  100 clients. Each client is connected with a TCP connection and for each client that is
  connected, a thread will be started using the function listenToClient.

  The listenToClient function will listen for commands from the client.
  Depending on the command, the server will take actions appropriately.
  The server expects that clients looking to download will connect first
  and when the downloader does so, an entry in the clientConnectionDict dictionary will be added,
  which will be used to connect downloaders and uploaders. When an uploader client connects
  and sends a command, the command is immediately followed by the data stream file (assuming
  that a downloader is already waiting to receive the file). When both an uploader and
  downloader are present using the same key, the packets from the uploader are then transmitted
  to the server, which are then sent to the downloader. The server acts as a mediator.
  When a termination command is sent to the server, the server will terminate as soon as all
  on going file transmissions are finished.

client.py
  The client will use the input parameters to connect to the server and send a command to
  the server. Depending on the command it will either terminate, download, or upload to the
  server.  
