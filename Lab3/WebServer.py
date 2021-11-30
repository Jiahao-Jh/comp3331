#coding: utf-8
from socket import *
import sys 
import os
#using the socket module

#Define connection (socket) parameters
#Address + Port no
#Server would be running on the same host as Client
# change this port number if required
if len(sys.argv) != 2:
    print("usage: python3 WebServer.py portnumber")
    exit(0)
serverPort = sys.argv[1]

serverSocket = socket(AF_INET, SOCK_STREAM)
#This line creates the serverâ€™s socket. The first parameter indicates the address family; in particular,AF_INET indicates that the underlying network is using IPv4.The second parameter indicates that the socket is of type SOCK_STREAM,which means it is a TCP socket (rather than a UDP socket, where we use SOCK_DGRAM).

serverSocket.bind(('localhost', int(serverPort)))
#The above line binds (that is, assigns) the port number 12000 to the serverâ€™s socket. In this manner, when anyone sends a packet to port 12000 at the IP address of the server (localhost in this case), that packet will be directed to this socket.

serverSocket.listen(1)
#The serverSocket then goes in the listen state to listen for client connection requests. 

print("The server is ready to receive\n")

while 1:
    connectionSocket, addr = serverSocket.accept()
#When a client knocks on this door, the program invokes the accept( ) method for serverSocket, which creates a new socket in the server, called connectionSocket, 
# dedicated to this particular client. The client and server then complete the handshaking, creating a TCP connection between the clientâ€™s 
# clientSocket and the serverâ€™s connectionSocket. With the TCP connection established, the client and server can now send bytes to each other over the connection.
#  With TCP, all bytes sent from one side not are not only guaranteed to arrive at the other side but also guaranteed to arrive in order

    request = connectionSocket.recv(1024).decode()
#wait for data to arrive from the client
    headers = request.split('\n')
    request_method = headers[0].split()[0]
    request_filename = headers[0].split()[1]
    #GET /index.html HTTP/1.1
    #GET /myimage.png HTTP/1.1
#change the case of the message received from client
    response = ""
    mes = bytes()
    if request_method == "GET":

            if request_filename == "/index.html":
                f = open("index.html")
                content = f.read()
                f.close()
                #+ "Content-Type: text/html\n" + "Content-Length: " + str(os.stat('index.html').st_size) +"\r\n"
                response = "HTTP/1.0 200 OK\n"+ "Content-Type: text/html\n"+ "Content-Length: " + str(len(content))  +"\n\n" + content
                mes = response.encode()
                print("file request success")

            elif request_filename == "/myimage.png":
                f = open("myimage.png",'rb')
                image_content = f.read()
                f.close()
                #file_size = os.stat('index.html').st_size
                response = "HTTP/1.0 200 OK\n" + "Content-Type: image/png\n" + "Content-Length: " + str(len(image_content)) + "\n\n"
                mes = response.encode()+image_content
                print("file request success")
            else:
                response = "HTTP/1.0 404 NOT FOUND\n\nFile Not Found"
                mes = response.encode()
                print("file request failed")


    else:
        print("Can't only handle GET request")

    connectionSocket.send(mes)
#and send it back to client

    connectionSocket.close()
#close the connectionSocket. Note that the serverSocket is still alive waiting for new clients to connect, we are only closing the connectionSocket.
