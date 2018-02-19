#!/usr/bin/env python3
# Import Needed Libraries
import socket # Primary Network Connection
import os # Forcommand line execution
import threading # Conncurrent client connections
import datetime # Used for logging
import subprocess # Used for Subprocessing
import re # For RegExpressions

# Import primary configuration File
server_config_file="../web_etc/server.config"
app_config_file="../web_etc/app.config"
exec(open(server_config_file).read())
exec(open(app_config_file).read())
# Parse ConfigFile Variables
WEBAPP_ROOT = WEBAPP_ROOT.rstrip('/')
#print("WEBAPP_ROOT: "+ WEBAPP_ROOT)
##########################################################
### Set Global Variables
log_date = datetime.datetime.now().strftime("%Y_%m_%d")

###### Primary functions

def getHeaders(http_req):
	exportList=''
	splitreq = http_req.split("\n")
	headerlist = []
	headernum = 1
	while splitreq[headernum] != "\r":
		headerparts = splitreq[headernum].split(":")
		if(len(headerparts) == 3):
			headerparts[1] = headerparts[1]+':'+headerparts[2]
		for hmap in HTTP_BASH_MAP:
			if(hmap[0] == headerparts[0]):
				headerparts[1]=(headerparts[1].strip('\r')).strip()
				exportList += "export %s='%s'; " % (hmap[1],headerparts[1])
				headerlist.append(hmap[1])
		headernum += 1
	return exportList;

def getCGIHeaders(http_req):
	exportList=''
	splitreq = http_req.split("\\n")
	headerlist = []
	headernum = 1
	while headernum < len(splitreq):
		headerparts = splitreq[headernum].split(": ")
		for hmap in HTTP_BASH_MAP:
			if(hmap[0] == headerparts[0]):
				headerparts[1]=(headerparts[1].strip('\\r')).strip()
				exportList += "export %s='%s'; " % (hmap[1],headerparts[1])
		headernum += 1
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
	

def processMethod(reqMethod,exportHeaderList,fullFilePath):
	if(reqMethod == 'GET'):
		runscript = "%s export REQUEST_METHOD='%s';" % (exportHeaderList, reqMethod)
		runscript = "export GATEWAY_INTERFACE='CGI/1.1';"
		runscript += " export REQUEST_METHOD='%s';" % (reqMethod)
		runscript += " export SCRIPT_FILENAME='%s';"  % (fullFilePath)
		runscript += " export SERVER_PROTOCOL='HTTP/1.1';"
		runscript += " export REDIRECT_STATUS='HTTP/1.1';"
		#runscript += " export CONTENT_TYPE='application/x-www-form-urlencoded';"
		#runscript += " export CONTENT_TYPE='text/html';"
		runscript += " export REMOTE_HOST='%s';" %('127.0.0.1')
		runscript += " export HTTP_HOST='%s';" %('127.0.0.1')
		#if()		
		#runscript += "export QUERY_STRING='%s';" (uriparts[1])
		runscript += "php-cgi -f %s"  % (fullFilePath)
		try:
			body = str(subprocess.check_output(runscript,stderr=subprocess.STDOUT,shell=True))
			body = body.strip('^b"').split("\\r\\n\\r\\n")
			moreHeaderList = getCGIHeaders(body[0])
			subprocess.check_output(moreHeaderList,stderr=subprocess.STDOUT,shell=True)
			body = str(body[1].replace("\\n",""))
			#print(body)
			statusCode='200'
		except Exception as e:
			print(e)
			statusCode='500'
	elif(reqMethod == 'PUT'):
		pass
	elif(reqMethod == 'OPTIONS'):
		pass
	elif(reqMethod == 'HEAD'):
		pass
	elif(reqMethod == 'POST'):
		pass
	elif(reqMethod == 'DELETE'):
		pass
	elif(reqMethod == 'TRACE'):
		pass
	elif(reqMethod == 'CONNECT'):
		pass
	else:
		body=''
		statusCode='400'
	return(statusCode,body)


def getfile(http_req):
	splitreq = http_req.split("\n")
	print(splitreq)
	return splitreq[1].split(" ")[1]
	
def processRequest(clientRequest):
	splitreq = clientRequest.split("\n")
	method = str(splitreq[0].split(" ")[0]).strip()
	uri = str(splitreq[0].split(" ")[1]).strip()
	httpVersion = str(splitreq[0].split(" ")[2]).strip()
	print("Method: "+method)
	print("URI: "+uri)
	print("httpVersion: "+httpVersion)
	
	exportHeaderList = getHeaders(clientRequest)
	return processResponse(method,uri,httpVersion,exportHeaderList)

def processResponse(method,uri,httpVersion,exportHeaderList):
	if(uri[0] == '/'):
		uriparts = getVars(uri)
		fullFilePath=os.path.abspath(WEBAPP_ROOT+uriparts[0])
	# 505 Check
	if(httpVersion not in HTTP_VERSION_SUPPORT):
		statusCode='505'
	# 405 Check
	elif(method not in HTTP_METHODS):
		statusCode='405'
	elif(not(os.path.isfile(WEBAPP_ROOT+uriparts[0]))):
		statusCode='404'
	else:
		(statusCode,body) = processMethod(method,exportHeaderList,fullFilePath)
	
	if(statusCode != '200'):
		body="<b>"+statusCode+": </b>"+RESPONSE_CODES[statusCode]
	
	response="HTTP/1.1 %s %s\r\n\r\n" % (statusCode,RESPONSE_CODES[statusCode])
	footer="\r\n\r\n"
	return (response, body, footer)

def requestHandler(clientSock):
	clientReq=clientSock.recv(1024).decode()
	
	(response, body, footer) = processRequest(clientReq)
	
	fullResponse ="%s%s%s" % (response,body,footer)
	
	clientSock.send(fullResponse.encode())
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
                sock.listen(int(CONNECTIONS))

                while True:
                        print("Waiting for Connection...")
                        (client_socket,client_addr) = sock.accept()
                        # Start Threading Requests
                        threading.Thread(target=requestHandler, args=((client_socket,))).start()

        except (OSError,):
                print("Exception Caught")
                sock.close()
                pass

# Execute Server
main()
