#!/bin/python3
# Import Needed Libraries
import socket # Primary Network Connection
import os # Forcommand line execution
import threading # Conncurrent client connections
import datetime # Used for logging

# Import primary configuration File
config_file="../web_etc/server.config"
exec(open(config_file).read())
##########################################################
#### Set Global Variables
log_date = datetime.datetime.now().strftime("%Y_%m_%d")

###### Primary functions
# Function to log request
def log_request():
        time_stamp = datetime.datetime.now().strftime("%Y-%m-%d::%H:%M")

def debug_vars(val):
        if val:
                print("LISTEN_IP: " + LISTEN_IP)
                print("LISTEN_PORT: " + LISTEN_PORT)
                print("HTTP_METHODS: " + str(HTTP_METHODS))
                print("WEBAPP_ROOT: " + WEBAPP_ROOT)
                print("LOG_REQUEST_GOOD: " + LOG_REQUEST_GOOD)
                print("LOG_REQUEST_BAD: " + LOG_REQUEST_BAD)
                print("CONNETIONS: " + CONNECTIONS)

def processRequest(clientRequest):
        print(clientRequest)
        method=''
        uri=''
        httpVersion=''

        return processResponse()

def processResponse():
        response="HTTP/1.1 200 OK\r\n\r\n"
        body="<b>Hello</b> world"
        footer="\r\n\r\n"
        return (response, body, footer)

def requestHandler(clientSock):
        #print("Reached response Handler")
        clientReq=clientSock.recv(1024)

        (response, body, footer) = processRequest(clientReq)

        # Combine full reponse  
        fullResponse =bytes(("%s%s%s" % (response,body,footer)),'UTF-8')
        #print(fullResponse)    
        clientSock.send(fullResponse)
        clientSock.close()
        pass


# Primary code
def main():
        debug_vars(False)
        # Create socket for communication
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((LISTEN_IP,int(LISTEN_PORT)))

        try:
                #sock.listen(0)
                sock.listen(10)
                #sock.listen(int(CONNECTIONS))

                while True:
                        print("Waiting for Connection...")
                        (client_socket,client_addr) = sock.accept()
                        #print(client_addr[0])
                        #print(client_addr[1])
                        #print((client_socket,))        
                        # Start Threading Requests
                        threading.Thread(target=requestHandler, args=((client_socket,))).start()


        except (OSError,):
                print("Exception Caught")
                sock.close()
                pass

# Execute Server

main()

