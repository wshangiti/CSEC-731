#/bin/python3
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

def requestHandler(clientSock):
	response='HTTP/1.1 200 OK\r\n\r\n'
	body='<b>Hello</b> world'
	footer='\r\n\r\n'
	
	clientSock.send(response+body+footer)
	clientSock.close()

# Primary code
def main():
	debug_vars(False)
	# Create socket for communication
	sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	sock.bind((LISTEN_IP,int(LISTEN_PORT)))
	
	try:
		#s.listen(10)
		sock.listen(int(CONNECTIONS))

		while True:
			(client_socket,client_addr) = sock.accept()
			print(client_addr[0]+" "+client_addr[1])
			
			# Start Threating Requests
			threading.Thread(target=requestHandler, args=(client_socket,))
			

	except:
		print("Exception Caught")
		sock.close()	

# Execute Server
main()

