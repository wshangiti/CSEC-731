#!/usr/bin/env python3
# Import Needed Libraries
# 2018_02_20
import socket # Primary Network Connection
import os # Forcommand line execution
import threading # Conncurrent client connections
import datetime # Used for logging
import subprocess # Used for Subprocessing
import platform

# Import primary configuration File
server_config_file="../web_etc/server.config"
app_config_file="../web_etc/app.config"
exec(open(server_config_file).read())
exec(open(app_config_file).read())
# Parse ConfigFile Variables
WEBAPP_ROOT = WEBAPP_ROOT.rstrip('/')

#print("WEBAPP_ROOT: "+ WEBAPP_ROOT)
##########################################################
if(DEBUG):
    print(platform.python_version())
###### Primary functions

def getHeaders(http_req,reqMethod,fullFilePath,uriparts):
    splitreq = http_req.split("\n")
    headerlist = []
    headernum = 0

    while splitreq[headernum] != "\r":
        headerparts = splitreq[headernum].split(": ")
        for hmap in CGI_BASH_MAP:
            if(hmap[0] == headerparts[0]):
                headerparts[1]=(headerparts[1].strip('\r')).strip()
                headerlist.append(([hmap[1],headerparts[1]]))
                if(hmap[0] == 'User-Agent'):
                    userAgent = headerparts[1]
                else:
                    #userAgent = ''
                    pass
        headernum += 1
    headerlist += SERVER_EXPORTS
    if(len(uriparts) > 1):
        headerlist.append((['QUERY_STRING', uriparts[1]]))
    headerlist.append((['SCRIPT_FILENAME',fullFilePath]))
    headerlist.append((['REQUEST_METHOD', reqMethod]))


    return (headerlist,userAgent)

def getVars(uri):
    uriparts =uri.split('?')
    # if request is to root of directory use default Root Page
    if(uriparts[0] == '/'):
        uriparts[0] = uriparts[0]+DEFAULT_ROOT_PAGE
    return uriparts

def getfile(http_req):
    splitreq = http_req.split("\n")
    return splitreq[1].split(" ")[1]

def log_request(method,httpVersion,statusCode,uri,sourceIP,sourcePort,destIP,destPort,userAgent):
    time_stamp = datetime.datetime.now().strftime("%Y-%m-%d::%H:%M:%S")
    logstring="%s Source:%s:%s Destination:%s:%s \"%s %s\" %s %s \"%s\"\r\n" %(time_stamp,sourceIP,sourcePort,destIP,destPort,method,uri,httpVersion,statusCode,userAgent)
    # Determine Where to Log
    if (statusCode != '200'):
        file = open(LOG_REQUEST_BAD, "a")
        file.write(logstring)
        file.close()
    else:
        file = open(LOG_REQUEST_GOOD, "a")
        file.write(logstring)
        file.close()

def processMethod(reqMethod,exportHeaderList,fullFilePath,postBody,cgiParser):
    # Process Method
    if(reqMethod == 'HEAD'):
        executeMethod=''
        pass
    elif(reqMethod == 'GET' or reqMethod == 'POST'):
        if(reqMethod == 'GET'):
            executeMethod = "%s %s" % (cgiParser,fullFilePath)
        else: # IF POST
            exportHeaderList.append((['BODY', postBody]))
            executeMethod = "echo $BODY | %s" % cgiParser
    elif(reqMethod == 'PUT'):
        pass
    elif(reqMethod == 'OPTIONS'):
        acceptString = "Allow:"
        for meth in HTTP_METHODS:
            acceptString += " %s," % (meth)
        # REMOVE TRAILING COMMA
        acceptString = acceptString[:-1]
        if(DEBUG):
            print(acceptString)
        statusCode = '200'
        return (statusCode, body)
    elif(reqMethod == 'DELETE'):
        pass
    elif(reqMethod == 'TRACE'):
        pass
    elif(reqMethod == 'CONNECT'):
        pass
    else:
        statusCode='405'

    # Process Headers
    runscript = ''
    if(DEBUG):
        print(str(exportHeaderList))
    for hmap in exportHeaderList:
        if(DEBUG):
            print("export %s='%s'; " % (hmap[0], hmap[1]))
        runscript += "export %s='%s'; " % (hmap[0], hmap[1])
    runscript += executeMethod
    if(DEBUG):
        print("RUN SCRIPT\n\n%s\n\n" % str(runscript))

    try:
        body = str(subprocess.check_output(runscript, stderr=subprocess.STDOUT, shell=True),'UTF-8')
        origbody= body
        if (DEBUG):
            print("ORIGBODY: \n\n" + body)
        body = body.strip('^b"').split("\r\n\r\n")
        if (DEBUG):
            print("NEW STRIPPED BODY: " + str(body))

        body = str(body[1].replace("\n", ""))

        if(DEBUG):
            print("\n\n\nBODY: \n\n\n"+str(body))
            print("\n\n\nBODY LEN : %i" % len(body))


        statusCode = '200'
    except Exception as e:
        print(e)
        statusCode = '500'
        body = ''
        origbody = ''

    return(statusCode,body,origbody)

def processRequest(clientRequest):
    # Star spliting reuest
    splitreq = clientRequest.split("\n")
    method = str(splitreq[0].split(" ")[0]).strip()
    uri = str(splitreq[0].split(" ")[1]).strip()

    httpVersion = str(splitreq[0].split(" ")[2]).strip()
    uriparts = getVars(uri)

    if(method == "GET" or method == "POST"):
        cgiParser = DEFAULT_CGI[method]
    else:
        cgiParser = ''

    # Checks if URI = *; primarily for options request
    if(uri != "*"):
        fullFilePath = os.path.abspath(WEBAPP_ROOT + uriparts[0])
    else:
        fullFilePath = uri
    postBody = splitreq[-1]
    (exportHeaderList, userAgent) = getHeaders(clientRequest,method,fullFilePath,uriparts)

    if(DEBUG):
        print(str(splitreq[0]))
        print(str(splitreq))
        print("cgiParserCommand: "+ cgiParser)
        print("CLIENT REQUEST:\n\n" + clientRequest)
        print("POST BODY: "+ str(postBody))
        print("User Agent: " + userAgent)
        print("Method: "+method)
        print("URI: "+uri)
        print("httpVersion: "+httpVersion)
        print("fullFilePath: "+fullFilePath)
        print("uriparts: "+str(uriparts))
        print("NEW HEADER LIST:\n\n"+str(exportHeaderList))
    # 505 Check
    if (httpVersion not in HTTP_VERSION_SUPPORT):
        statusCode = '505'
    # 405 Check
    elif (method not in HTTP_METHODS):
        statusCode = '405'
    elif (not (os.path.isfile(WEBAPP_ROOT + uriparts[0]))):
        statusCode = '404'
    else:
        (statusCode, body, headers) = processMethod(method, exportHeaderList, fullFilePath, postBody,cgiParser)

    #If status code of request is not 'OK', then set response body
    if (statusCode != '200'):
        body = "<b>" + statusCode + ": </b>" + RESPONSE_CODES[statusCode]

    if (body == ''):
        response = "HTTP/1.1 %s %s\r\n" % (statusCode, RESPONSE_CODES[statusCode])
    else:
        response="HTTP/1.1 %s %s\r\n\r\n" % (statusCode,RESPONSE_CODES[statusCode])
    footer="\r\n\r\n"

    return (response, body, footer, method, httpVersion, statusCode, uri, userAgent,headers)

def requestHandler(clientSock):
    clientReq=clientSock.recv(1024).decode()
    sourceIP = clientSock.getpeername()[0]
    sourcePort=clientSock.getpeername()[1]
    destIP= clientSock.getsockname()[0]
    destPort= clientSock.getsockname()[1]

    print("Full Request is: \n\n%s\n-----------------------------" % clientReq)
    if(DEBUG):
        print("SOURCE IP: "+ sourceIP)

    (response, body, footer, method, httpVersion, statusCode, uri, userAgent, headers) = processRequest(clientReq)

    if(body == ''):
        fullResponse = "%s%s%s" % (response, headers, footer)
    else:
        fullResponse = "%s%s%s" % (response,body,footer)
    # Log Request to File

    print("Full Response is: \n\n%s\n-----------------------------" % fullResponse)
    log_request(method, httpVersion, statusCode, uri, sourceIP, sourcePort, destIP, destPort, userAgent)

    clientSock.send(fullResponse.encode())
    clientSock.close()
    pass


# Primary code
def main():
    # Create socket for communication
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    # Allows reuse of Socket Address
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Binds Socket
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
