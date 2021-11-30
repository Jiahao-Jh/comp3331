import socket
import sys 
import json
import threading
import time
BUFF_SIZE = 2048

#input check and convert arguments to int
if len(sys.argv) != 4:
    print("Usage: client.py server_IP server_port client_udp_server_port")
    exit(0)

server_ip = sys.argv[1]
server_port = sys.argv[2]
client_udp_port = sys.argv[3]

#check port number is decimal
if not server_port.isdecimal() or not client_udp_port.isdecimal():
    print("Usage: client.py server_IP server_port client_udp_server_port")
    exit(0)

#check IP address is vaild
try:
    socket.inet_aton(server_ip)
except :
    try:
        socket.inet_pton(socket.AF_INET6, server_ip)
    except:
        print("Usage: client.py server_IP server_port client_udp_server_port")
        exit(0)

server_port = int(server_port)

def udp_receive_thread():
    while 1:
        #first 2 trasmassion is for sender name and filename
        
        client_udp_socket.settimeout(None)
        message, clientAddress = client_udp_socket.recvfrom(BUFF_SIZE)
        sender_name = message.decode()
        message, clientAddress = client_udp_socket.recvfrom(BUFF_SIZE)
        received_filename = message.decode()
        filename = f"{sender_name}_{received_filename}"
        f = open(filename, "wb")
        try:
            while 1:
                client_udp_socket.settimeout(1)
                message, clientAddress = client_udp_socket.recvfrom(BUFF_SIZE)
                f.write(message)
        except socket.timeout:
            f.close()
            print(f"\nReceived {received_filename} from {sender_name}\nEnter one of the following commands ((MSG, DLT, EDT, RDM, ATU, OUT, UPD):",end="")



def udp_send_thread(filename,ip,udp):
        #send filename first
        client_udp_socket.sendto(username.encode(),(ip,udp))
        client_udp_socket.sendto(filename.encode(),(ip,udp))

        #read and send data as BUFF_SIZE chunk
        f = open(filename,'rb')
        udp_content = f.read(BUFF_SIZE)
        while(udp_content):
            if (client_udp_socket.sendto(udp_content,(ip,udp))):
                udp_content = f.read(BUFF_SIZE)
        print(f"\n{filename} has been uploaded\nEnter one of the following commands ((MSG, DLT, EDT, RDM, ATU, OUT, UPD):",end="")
        f.close()


#setup tcp socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.settimeout(10)
client_socket.connect((server_ip, server_port))
#get username and password
username = input("Username: ")
password = input("Password: ")

while 1:
    #Type = Login
    tmp_dict = {
        "Type": "Login",
        "Username": username,
        "Password": password,
        "UDPport": client_udp_port
    }
    message = json.dumps(tmp_dict)
    client_socket.sendall(message.encode())
    server_returned_data = client_socket.recv(BUFF_SIZE)
    login_status = server_returned_data.decode()

    if login_status == '1':
        #successful login
        print("Welcome to TOOM!")
        break
    elif login_status == '0':
        print("Invalid Password. Please try again")
        password = input("Password: ")
        continue
    elif login_status == '-1':
        print("Invalid Password. Your account has been blocked. Please try again later")
        password = input("Password: ")
        continue
    elif login_status == '-2':
        print("Your account is blocked due to multiple login failures. Please try again later")
        password = input("Password: ")
        continue

#setup udp socket
udp_port = int(client_udp_port)
ip_address = socket.gethostbyname(socket.gethostname())
client_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_udp_socket.bind((ip_address, udp_port))

#start udp receive thread
new_udp_thread=threading.Thread(target=udp_receive_thread)
new_udp_thread.daemon=True
new_udp_thread.start()

while 1:
    input_command = input("Enter one of the following commands ((MSG, DLT, EDT, RDM, ATU, OUT, UPD):")
    if input_command.split(" ")[0] == "MSG":
        tmp_dict = {
            "Type": "MSG",
            "Message": input_command[4:]
        }
        if tmp_dict["Message"] == "":
            print("Error. Invalid command!")
            continue
        message = json.dumps(tmp_dict)
        client_socket.sendall(message.encode())
        server_returned_message = client_socket.recv(BUFF_SIZE)
        print(server_returned_message.decode())

    elif input_command.split(" ")[0] == "DLT":
        #command check
        if len(command) != 6:
            print("Error. Invalid command!")
            continue
        command = input_command.split(" ")
        if not command[1].startswith("#"):
            print("Error. Invalid command!")
            continue
        tmp_dict = {
            "Type": "DLT",
            "Message_number": command[1][1:],
            "Timestamp": " ".join(command[2:])
        }

        message = json.dumps(tmp_dict)
        client_socket.sendall(message.encode())
        server_returned_message = client_socket.recv(BUFF_SIZE)
        dlt_status = server_returned_message.decode()

        message_number = tmp_dict["Message_number"]
        #success deleted
        if dlt_status.startswith("0"):
            timestamp = dlt_status[2:]        
            print(f"Message #{message_number} deleted at {timestamp}")
        #Invaild message number
        elif dlt_status == '1':
            print("Invaild message number")
        #Invaild timestamp
        elif dlt_status == '2':
            print("Invaild timestamp")
        #Unauthorised to delete Message
        elif dlt_status == '3':
            print(f"Unauthorised to delete Message #{message_number}")
    elif input_command.split(" ")[0] == "EDT":
        command = input_command.split(" ")
        if len(command) <= 6:
            print("Usage: EDT #message_number date mouth year hour/min/sec message")
            continue

        tmp_dict = {
            "Type": "EDT",
            "Message_number": command[1][1:],
            "Timestamp": " ".join(command[2:6]),
            "Edit_message": " ".join(command[6:])
        }
        message = json.dumps(tmp_dict)
        client_socket.sendall(message.encode())
        server_returned_message = client_socket.recv(BUFF_SIZE)
        edt_status = server_returned_message.decode()

        message_number = tmp_dict["Message_number"]
        #success deleted
        if edt_status.startswith("0"):
            timestamp = edt_status[2:]
            print(f"Message #{message_number} edited at {timestamp}")
        elif edt_status == '1':
            print("Invaild message number")
        elif edt_status == '2':
            print("Invaild timestamp")
        elif edt_status == '3':
            print(f"Unauthorised to edit Message #{message_number}")
    
    elif input_command.split(" ")[0] == "RDM":
        command = input_command.split(" ")
        if len(command) != 5:
            print("Usage: RDM date mouth year hour/min/sec")
            continue
        timestamp = input_command[4:]

        tmp_dict = {
            "Type": "RDM",
            "Timestamp": timestamp
        }  
        message = json.dumps(tmp_dict)
        client_socket.sendall(message.encode())
        server_returned_message = client_socket.recv(BUFF_SIZE)
        rdm_status = server_returned_message.decode()   


        if rdm_status == "1":
            print(f"No new message since {timestamp}")
        else:
            print(rdm_status.strip())

    elif input_command.split(" ")[0] == "ATU":
        command = input_command.split(" ")
        if len(command) != 1:
            print("Usage: ATU")
            continue
        tmp_dict = {
            "Type": "ATU",
        }  
        message = json.dumps(tmp_dict)
        client_socket.sendall(message.encode())
        server_returned_message = client_socket.recv(BUFF_SIZE)
        atu_status = server_returned_message.decode()   

        if atu_status == "1":
            print("No other active user")
        else:
            print(atu_status.strip())



    elif input_command.split(" ")[0] == "UPD":
        command = input_command.split(" ")
        if len(command) != 3:
            print("Usage: UPD username filename")
            continue
        filename = command[2]

        tmp_dict = {
            "Type": "UPD",
            "UDP_name": command[1]
        }  
        message = json.dumps(tmp_dict)
        client_socket.sendall(message.encode())
        server_returned_message = client_socket.recv(BUFF_SIZE)
        udp_status = server_returned_message.decode()   
        if udp_status == '-1':
            print(command[1] + " is offine.")
            continue
        ip = udp_status.split(" ")[0]
        udp = udp_status.split(" ")[1]

        udp = int(udp)

        new_udp_thread=threading.Thread(target=udp_send_thread,args=(filename,ip,udp,))
        new_udp_thread.daemon=True
        new_udp_thread.start()   

    elif input_command == "OUT":
        tmp_dict = {
            "Type": "OUT"
        }
        message = json.dumps(tmp_dict)
        client_socket.sendall(message.encode())
        server_returned_message = client_socket.recv(BUFF_SIZE)
        print(server_returned_message.decode())
        break
    else:
        print("Error. Invalid command!")
        continue

client_socket.close()
client_udp_socket.close()