import socket
import sys 
import time
import json
from datetime import datetime
import threading

BUFF_SIZE = 2048
#input check and convert arguments to int
if len(sys.argv) != 3:
    print("Usage: server.py server_port number_of_consecutive_failed_attempts")
    exit(0)

server_port = sys.argv[1]
number_attempts = sys.argv[2]

#check port number is decimal
if not server_port.isdecimal() or not number_attempts.isdecimal():
    print("Usage: server.py server_port number_of_consecutive_failed_attempts")
    exit(0)

server_port = int(server_port)
number_attempts = int(number_attempts)

if number_attempts not in range(1,5):
    print(f"Invalid number of allowed failed consecutive attempt: {number_attempts}. The valid value of argument number is an integer between 1 and 5")
    exit(0)

#perpare files
#empty log files
open('userlog.txt', 'w').close()
open('messagelog.txt', 'w').close()

#function
#active_users = [ User_info ]
def writeToUserLog(username, ip, udpport):
    f = open("userlog.txt","a")
    timestamp = datetime.now().strftime("%d %b %Y %H:%M:%S")
    user_number = len(active_users)+1
    User_info = {
        "number": user_number,
        "timestamp": timestamp,
        "username": username,
        "ip": ip,
        "udpport": udpport
    }
    active_users.append(User_info)

    f.write(f"{user_number}; {timestamp}; {username}; {ip}; {udpport}\n")
    f.close()

def rewriteUserLog():
    f = open("userlog.txt","w")
    for i in active_users:
        user_number = i["number"]
        timestamp = i["timestamp"]
        username = i["username"]
        ip = i["ip"]
        udpport = i["udpport"]
        f.write(f"{user_number}; {timestamp}; {username}; {ip}; {udpport}\n")
    f.close()

#user_messages = [ User_message ]
def writeToMessageLog(username, message):
    f = open("messagelog.txt","a")
    tmp = datetime.now()
    timestamp = tmp.strftime("%d %b %Y %H:%M:%S")
    message_number = len(user_messages)+1
    User_message = {
        "number": message_number,
        "timestamp": timestamp,
        "username": username,
        "message": message,
        "edited": False
    }
    user_messages.append(User_message)

    f.write(f"{message_number}; {timestamp}; {username}; {message}\n")  
    f.close()
    return message_number,timestamp

def rewriteMessageLog():
    f = open("messagelog.txt","w")
    for i in user_messages:
        message_number = i["number"]
        timestamp = i["timestamp"]
        username = i["username"]
        message = i["message"]
        if i["edited"] == True:
            f.write(f"{message_number}; {timestamp}; {username}; {message}; yes\n")  
        else:
            f.write(f"{message_number}; {timestamp}; {username}; {message}\n")  
    f.close()


#multi-thread function
#thread_lock = threading.Lock()
def process_command(socket_threading,addr):
    while 1:
        message = socket_threading.recv(BUFF_SIZE)
        client_input_data = json.loads(message.decode())
        
        input_type = client_input_data["Type"]
        #check input type
        if input_type == "Login":
            #check login
            #assume username is uniq and not equal to ""
            return_data = "0"
            for i in credentials_dict.keys():
                if client_input_data["Username"] == i:
                    login_time = datetime.now().strftime("%d %b %Y %H:%M:%S")
                    client_username = ""
                    #blocked
                    if credentials_dict[i]["user_status"] != 0 and credentials_dict[i]["user_status"] > time.time() :
                        print(f"{client_username} attmpts to login at {login_time}. Get blocked.")
                        return_data = "-2"
                    #successful
                    elif client_input_data["Password"] == credentials_dict[i]["password"]:
                        return_data = "1"
                        client_username = i
                        credentials_dict[i]["invaild_attempts"] = 0
                        writeToUserLog(i,addr[0],client_input_data["UDPport"])
                        
                        print(f"{client_username} login at {login_time}.")
                    #tiger blocked
                    else:
                        print(f"{client_username} attmpts to login at {login_time}. Failed to many times.")
                        credentials_dict[i]["invaild_attempts"] += 1
                        if credentials_dict[i]["invaild_attempts"] >= number_attempts:
                            return_data = "-1"
                            credentials_dict[i]["user_status"] = time.time() + 10

            # only invaild user password, invaild username have no consequence            

            socket_threading.sendall(return_data.encode())

        elif input_type == "MSG":
            message = client_input_data["Message"]
            message_number,timestamp = writeToMessageLog(client_username,client_input_data["Message"])
            print(f"{client_username} posted MSG #{message_number} \"{message}\" at {timestamp}." )
            return_message = f"Message #{message_number} posted at {timestamp}."
            socket_threading.sendall(return_message.encode())

        elif input_type == "DLT":
            return_data = "0"
            dlt_message_number = client_input_data["Message_number"]
            dlt_message_number = int(dlt_message_number)

            deleted_message_time = datetime.now().strftime("%d %b %Y %H:%M:%S")
            if dlt_message_number > len(user_messages) or dlt_message_number <= 0:
                # invaild message number provide
                print(f"{client_username} attempts to edit MSG #{dlt_message_number} at {deleted_message_time}. Invaild message number provide.")
                return_data = "1"
            elif user_messages[dlt_message_number-1]["timestamp"] != client_input_data["Timestamp"] :
                # invaild timestamp provide
                print(f"{client_username} attempts to edit MSG #{dlt_message_number} at {deleted_message_time}. Invaild timestamp provide.")
                return_data = "2"
            elif user_messages[dlt_message_number-1]["username"] != client_username :
                # Unauthorised to delete Message #3
                print(f"{client_username} attempts to edit MSG #{dlt_message_number} at {deleted_message_time}. Authorisation fails.")
                return_data = "3"
            else:
                #successful delete, return data startswith 0
                user_messages.remove(user_messages[dlt_message_number-1])
                for i in user_messages:
                    if i["number"] > dlt_message_number-1:
                        i["number"] = i["number"] - 1
                rewriteMessageLog()
                deleted_message = user_messages[dlt_message_number-1]["message"]
                
                print(f"{client_username} deleted MSG #{dlt_message_number} \"{deleted_message}\" at {deleted_message_time}.")
                return_data = f"0 {deleted_message_time}"

            socket_threading.sendall(return_data.encode())
        elif input_type == "EDT":
            return_data = "0"
            edt_message_number = client_input_data["Message_number"]
            edt_message_number = int(edt_message_number)

            edt_message_time = datetime.now().strftime("%d %b %Y %H:%M:%S")
            if edt_message_number > len(user_messages) or edt_message_number <= 0:
                # invaild message number provide
                print(f"{client_username} attempts to edit MSG #{edt_message_number} at {edt_message_time}. Invaild message number provide.")
                return_data = "1"
            elif user_messages[edt_message_number-1]["timestamp"] != client_input_data["Timestamp"] :
                # invaild timestamp provide
                print(f"{client_username} attempts to edit MSG #{edt_message_number} at {edt_message_time}. Invaild timestamp provide.")
                return_data = "2"
            elif user_messages[edt_message_number-1]["username"] != client_username :
                # Unauthorised to edit Message #3
                print(f"{client_username} attempts to edit MSG #{edt_message_number} at {edt_message_time}. Authorisation fails.")
                return_data = "3"
            else:
                #successful edit, return data startswith 0
                edt_message = client_input_data["Edit_message"]
                user_messages[edt_message_number-1]["edited"] = True
                user_messages[edt_message_number-1]["message"] = edt_message
                rewriteMessageLog()

                print(f"{client_username} edited MSG #{edt_message_number} \"{edt_message}\" at {edt_message_time}.")
                return_data = f"0 {edt_message_time}"

            socket_threading.sendall(return_data.encode())

        elif input_type == "RDM":
            timestamp = client_input_data["Timestamp"]
            client_datetime = datetime.strptime(timestamp, '%d %b %Y %H:%M:%S')
            result_list = []
            return_data = ""

            for i in user_messages:
                message_datetime = datetime.strptime(i["timestamp"], '%d %b %Y %H:%M:%S')
                if client_datetime < message_datetime:
                    result_list.append(i)
            if len(result_list) ==0:
                return_data="1"
                socket_threading.sendall(return_data.encode())
                continue
                # User_message = {
                #     "number": message_number,
                #     "timestamp": timestamp,
                #     "username": username,
                #     "message": message,
                #     "edited": False
                # }
            for i in result_list:
                n = i["number"]
                u = i["username"]
                m = i["message"]
                t = i["timestamp"]
                if i["edited"] == True:
                    return_data = return_data + f"#{n}, {u}: {m}, edited at {t}.\n"
                else:
                    return_data = return_data + f"#{n}, {u}: {m}, posted at {t}.\n"
            socket_threading.sendall(return_data.encode())

            print(f"Return message:\n{return_data}")

        elif input_type == "ATU":
            result_list = []
            return_data = ""

            # User_info = {
            #     "number": user_number,
            #     "timestamp": timestamp,
            #     "username": username,
            #     "ip": ip,
            #     "udpport": udpport
            # }
            for i in active_users:
                if client_username != i["username"]:
                    result_list.append(i)
            if len(result_list) ==0:
                return_data="1"
                socket_threading.sendall(return_data.encode())
                continue
            for i in result_list:
                u = i["username"]
                ip = i["ip"]
                udp = i["udpport"]
                t = i["timestamp"]
                return_data = return_data + f"{u}, {ip}, {udp}, active since {t}.\n"

            socket_threading.sendall(return_data.encode())
            print(f"Return active user list:\n{return_data}")
        elif input_type == "UPD":
            udp_name = client_input_data["UDP_name"]
            return_data="-1"
            for i in active_users:
                if udp_name == i["username"]:
                    return_data= i["ip"] + " " + i["udpport"]

            socket_threading.sendall(return_data.encode())        

        elif input_type == "OUT":
            return_message = f"Bye, {client_username}!"
            socket_threading.sendall(return_message.encode())
            
            user_number = 0
            for i in range(len(active_users)):
                if active_users[i]["username"] == client_username:
                    user_number = i
                    break
            active_users.remove(active_users[user_number])
            for i in active_users:
                if i["number"] > user_number+1:
                    i["number"] = i["number"] -1    
            rewriteUserLog()
            print(f"{client_username} logout")
            break
    socket_threading.close()

#generate dic from credentials file
# {
# username: {
# 'password': password,
# 'user_status': status_code, # default 0
# 'invaild_attempts': num, # default 0
# 
# }
# }

f = open("credentials.txt","r")
user_data = f.read().strip().replace(' ', '\n').split('\n')
credentials_dict = {}
tmp_dict = {}
for i in range(len(user_data)):
    if i % 2 == 1:
        credentials_dict[user_data[i-1]] = {'password': user_data[i],'user_status': 0,'invaild_attempts': 0}

user_messages = []
active_users = []

#setup socket
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip_address = socket.gethostbyname(socket.gethostname())

serverSocket.bind((ip_address, server_port))

serverSocket.listen(5) 

#won't limit number of user
while 1:
    connectionSocket, addr = serverSocket.accept()

    new_thread=threading.Thread(target=process_command, args=(connectionSocket,addr))
    new_thread.daemon=True
    new_thread.start()



serverSocket.close()

