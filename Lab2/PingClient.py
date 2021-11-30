#python3
#coding: utf-8
from socket import *
import time
import sys
#Define connection (socket) parameters
#Address + Port no
#Server would be running on the same host as Client
serverName =  sys.argv[1]

#change this port number if required
serverPort = int(sys.argv[2])

clientSocket = socket(AF_INET, SOCK_DGRAM)

rtt = []
#This line creates the clientâ?????s socket. The first parameter indicates the address family; in particular,AF_INET indicates that the underlying network is using IPv4.The second parameter indicates that the socket is of type SOCK_DGRAM,which means it is a UDP socket (rather than a TCP socket, where we use SOCK_STREAM).

for i in range(15):
    num = 3331
    message = f"PING {num} time \r\n"
    print(f"{num} PING to {serverName}, seq = {i}, ",end = "")
    send_time = time.time()
#input() is a built-in function in Python. When this command is executed, the user at the client is prompted with the words â?????Input lowercase sentence:â???? The user then uses the keyboard to input a line, which is put into the variable sentence. Now that we have a socket and a message, we will want to send the message through the socket to the destination host.

    clientSocket.sendto(message.encode('utf-8'),(serverName, serverPort))
# Note the difference between UDP sendto() and TCP send() calls. In TCP we do not need to attach the destination address to the packet, while in UDP we explicilty specify the destination address + Port No for each message
    clientSocket.settimeout(0.6)
    try:
        modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
    except:
        print('rtt = time out')
# Note the difference between UDP recvfrom() and TCP recv() calls.
    recv_time = time.time()
    if recv_time - send_time < 0.6:
        rtt_time = round((recv_time - send_time) * 1000)
        print(f"rtt = {rtt_time} ms")
        rtt.append(rtt_time)


# print the received message
    num +=1
print("\n\n")
print(f"Minimum RTT = {min(rtt)} ms")
print(f"Maximum RTT = {max(rtt)} ms")
print(f"Average RTT = {round(sum(rtt)/len(rtt))} ms")
print(f"{round((len(rtt)/15)*100,1)}% of packets have been lost through the network")
clientSocket.close()
# Close the socket
