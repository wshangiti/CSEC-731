#!/usr/bin/env python3
# Import Needed Libraries
import socket # Primary Network Connection
import os # Forcommand line execution
import threading # Conncurrent client connections
import datetime # Used for logging
import subprocess # Used for Subprocessing

# Import primary configuration File
config_file="../web_etc/server.config"
exec(open(config_file).read())
# Parse ConfigFile Variables
WEBAPP_ROOT = WEBAPP_ROOT.rstrip('/')
#print("WEBAPP_ROOT: "+ WEBAPP_ROOT)
##########################################################
### Set Global Variables
log_date = datetime.datetime.now().strftime("%Y_%m_%d")

RESPONSE_CODES={
        '200':'OK',
        '400':'Bad Request',
        '401':'Unauthorized',
        '403':'Forbidden',
        '404':'Not Found',
        '405':'Method Not Allowed',
        '411':'Length Required',
        '500':'Internal Server Error',
        '505':'HTTP Version not supported'
        }
HTTP_BASH_MAP={
	'gwi':'GATEWAY_INTERFACE',
	'sfn':'SCRIPT_FILENAME',
 	'rqm':'REQUEST_METHOD',
 	'sp':'SERVER_PROTOCOL',
	'rh':'REMOTE_HOST',
 	'Accept':'CONTENT_TYPE',
 	'Host':'HTTP_HOST',
 	'cl':'CONTENT_LENGTH',
 	'bdy':'BODY'
}


###### Primary functions
# Function to log requesti
#def getmethod(http_req):
#	splitreq = http_req.split("\n")
#	method = str(splitreq[0].split(" "))
#	print("GetMethod: SplitReq: "+str(splitreq))
#	print("GetMethod: "+method)
#	return method

#def getfile(http_req):
#	splitreq = http_req.split("\n")
#	print("GetFile: SplitReq: "+str(splitreq))
#	return splitreq[0].split(" ")[1]

def getHeaders(http_req):
	exportList=''
	splitreq = http_req.split("\n")
	#print (splitreq)
	#exit(0)
	headerlist = []
	headernum = 1
	while splitreq[headernum] != "\r":
		#print("HeaderNum: " + str(headernum))
		#print("HeaderSplit: " + splitreq[headernum])
		headerparts = splitreq[headernum].split(": ")
		#print("Key: %s, Value: %s" % (headerparts[0], headerparts[1]))
		for hmap in HTTP_BASH_MAP:
			if(hmap == headerparts[0]):
				print("Map is: " + hmap)
				print("%s=%s" % (headerparts[0], headerparts[1]))
				print('export %s=\'%s\';' % (HTTP_BASH_MAP[hmap],headerparts[1]))
				exportList += ("export %s=\'%s\';" % (HTTP_BASH_MAP[hmap],headerparts[1]))
		#headernum=headernum+1
		#headerlist.append(spitreq[headernum])
		#print("%s=%s" % (headerparts[0], headerparts[1]))
		headernum += 1
	#return headerlist
	print("##########################################################")
	print(str(exportList))
	print("##########################################################")
	exit(0)
	return exportList;

def getVars(uri):
	uriparts =uri.split('?')
	return uriparts

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
                print("HTTP_VERSION_SUPPORT: " + str(HTTP_VERSION_SUPPORT))

def processMethod(reqMethood):
        switcher = {
        "GET": "January",
        "POST": "February",
        "PUT": "March",
        "DELETE": "April",
        "CONNECT": "May",
        }
        switcher.get(reqMethood, "METHOD REQUEST NOT SUPPORTED")

def getfile(http_req):
	splitreq = http_req.split("\n")
	print(splitreq)
	return splitreq[1].split(" ")[1]
	
#def getHeaders(http_req):
#	print(http_req)
#	splitreq = http_req.split("\n")
#	headerlist = []
#	headernum = 1
#	while splitreq[headernum] != "\r":
#		headerlist.append(splitreq[headernum])
#		headernum = headernum+1
#		headerparts = splitreq[headernum].split(":")
#		print("Key: %s, Value: %s" % (headerparts[0], headerparts[1]))
#		print("%s=%s" % (headerparts[0], headerparts[1]))
#	return headerlist

def processRequest(clientRequest):
	splitreq = clientRequest.split("\n")
	#print("GetMethod: SplitReq: "+str(splitreq))
	method = str(splitreq[0].split(" ")[0]).strip()
	uri = str(splitreq[0].split(" ")[1]).strip()
	httpVersion = str(splitreq[0].split(" ")[2]).strip()
	print("Method: "+method)
	print("URI: "+uri)
	print("httpVersion: "+httpVersion)
	
	#exportHeaderList = getHeaders(clientRequest)
	exportHeaderList = ''
	#print(str(exportHeaderList))
	#exit(0)
	#return method
	#print(getHeaders(str(clientRequest,'UTF-8')))
	#method=getmethod(http_req)
	#uri=''
	#httpVersion=''
	return processResponse(method,uri,httpVersion,exportHeaderList)

def processResponse(method,uri,httpVersion,exportHeaderList):
	#httpVersion = 'bob'
	if(uri[0] == '/'):
		uriparts = getVars(uri)
	# 505 Check
	if(httpVersion not in HTTP_VERSION_SUPPORT):
		statusCode='505'
	# 405 Check
	elif(method not in HTTP_METHODS):
		statusCode='405'
	elif(not(os.path.isfile(WEBAPP_ROOT+uriparts[0]))):
		statusCode='404'
	else:
		statusCode='200'
		print("Method Supported.")
	
	reasonPhrase=RESPONSE_CODES[statusCode]
	#print(reasonPhrase)
	response=("HTTP/1.1 %s %s\r\n\r\n" % (statusCode,reasonPhrase))
	print("Response is : "+ response)
	#response=("HTTP/1.1 200 OK\r\n\r\n"
	if(statusCode == '200'):
		#runscript = "%s export REQUEST_METHOD='%s';" (exportHeaderList, method)
		runscript = "export GATEWAY_INTERFACE='CGI/1.1';"
		runscript += "export REQUEST_METHOD='%s';" % (method)
		runscript += "export SCRIPT_FILENAME='%s%s';"  % (WEBAPP_ROOT,uriparts[0])
		runscript += "export SERVER_PROTOCOL='HTTP/1.1';"
		runscript += "export REDIRECT_STATUS='HTTP/1.1';"
		runscript += "export CONTENT_TYPE='application/x-www-form-urlencoded';"
		runscript += "export REMOTE_HOST='%s';" %('127.0.0.1')
		runscript += "export HTTP_HOST='%s';" %('127.0.0.1')
		#runscript += "export QUERY_STRING='%s';" (uriparts[1])
		runscript = "php-cgi -f %s%s"  % (WEBAPP_ROOT,uriparts[0])
		body = subprocess.check_output(runscript,shell=True,stderr=subprocess.STDOUT)
		
		#body="<b>Hello</b> world"
	else:
		body="<b>"+statusCode+": </b>"+reasonPhrase
		
	footer="\r\n\r\n"
	return (response, body, footer)

def requestHandler(clientSock):
        #print("Reached response Handler")
	clientReq=str(clientSock.recv(1024),'UTF-8')	
	#method= getmethod(clientReq)
	#file = getfile(clientReq)
	#elist = getHeaders(clientReq)
	#print("Method: " + method)
	#print("Headers: " + elist)
	#headers = getHeaders(request)
	#print("File: " + uriparts[0])
	#print("Vars: " + uriparts[1])
	#runscript = "%s export REQUEST_METHOD='%s';" (elist, method)
	#runscript += "export QUERY_STRING='%s';" (vars)
	#runscript += "export SCRIPT_FILENAME='%s%s';"  % (doc_root,uriparts[0])
	#runscript += "php-cgi -f %s%s"  % (doc_root,uriparts[0])
	

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
