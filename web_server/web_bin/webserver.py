#!/usr/bin/env python3
# Import Needed Libraries
import socket # Primary Network Connection
import os # Forcommand line execution
import threading # Conncurrent client connections
import datetime # Used for logging
import subprocess # Used for Subprocessing
import platform # Python Version Debugging

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
    userAgent = ''


    if(len(splitreq) == '1'):
        pass
    else:
        #while splitreq[headernum] != "\r":
        while((headernum < len(splitreq)) and (splitreq[headernum] != "\r")):
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

def processMethod(reqMethod,exportHeaderList,fullFilePath,reqBody,cgiParser,uri):
    # Process Method
    headers=''
    body=''
    executeMethod=''
    runscript = ''
    # Bas Request by default
    statusCode='400'
    # Add additional Headers
    if(reqMethod == 'POST'):
        exportHeaderList.append((['BODY', reqBody]))

    if(DEBUG):
        print(str(exportHeaderList))
    for hmap in exportHeaderList:
        if(DEBUG):
            print("export %s='%s'; " % (hmap[0], hmap[1]))
        runscript += "export %s='%s'; " % (hmap[0], hmap[1])

    if(DEBUG):
        print(runscript)
    # Parse Header Requests
    # ----- HEAD -------

    if(reqMethod == 'HEAD'):
        try:
            subprocess.check_output(runscript, stderr=subprocess.STDOUT, shell=True)
        except Exception as e:
            print(e)
            statusCode = '500'
    # ----- GET/POST -------
    elif(reqMethod == 'GET' or reqMethod == 'POST'):
        if (not (os.path.isfile(fullFilePath))):
            statusCode = '404'
        else:
            if(reqMethod == 'GET'):
                executeMethod = "%s %s" % (cgiParser,fullFilePath)
            else: # IF POST
                executeMethod = "echo $BODY | %s" % cgiParser
            runscript += executeMethod
            try:
                body = str(subprocess.check_output(runscript, stderr=subprocess.STDOUT, shell=True),'UTF-8')
                headers= body
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
    # ----- PUT -------
    elif(reqMethod == 'PUT'):
        print(runscript)
        if( 'CONTENT_LENGTH' not in runscript):
            statusCode = '411'
        else:
            executeMethod = "echo '%s' > %s" % (reqBody,fullFilePath)
            runscript += executeMethod
            print(runscript)
            try:
                subprocess.check_output(runscript, stderr=subprocess.STDOUT, shell=True)
                body="OK"
                statusCode = '200'
            except:
                statusCode = '403'
    # ----- OPTIONS -------
    elif(reqMethod == 'OPTIONS'):
        acceptString = "Allow:"
        for meth in HTTP_METHODS:
            acceptString += " %s," % (meth)
        # REMOVE TRAILING COMMA
        acceptString = acceptString[:-1]
        if(DEBUG):
            print(acceptString)
        headers = acceptString
        statusCode = '200'
    # ----- DELETE -------
    elif(reqMethod == 'DELETE'):
        if (not (os.path.isfile(fullFilePath))):
            statusCode = '404'
        else:
            executeMethod = "rm -f %s" % (fullFilePath)
            runscript += executeMethod
            print(executeMethod)
            try:
                subprocess.check_output(runscript, stderr=subprocess.STDOUT, shell=True)
                statusCode = '200'
            except:
                # Permission Denied
                statusCode = '403'
    # ----- TRACE -------
    elif(reqMethod == 'TRACE'):
        statusCode = '200'
    # ----- CONNECT -------temp.txt
    elif(reqMethod == 'CONNECT'):
        print('**************\n\nURI:'+ uri)
        if(uri.startswith('http://')):
            reqUri=uri.strip('http://')
        elif(uri.startswith('https://')):
            reqUri=uri.strip('https://')
        else:
            reqUri=uri

        print('**************\n\nreqUri:' + reqUri)

        if(':' in reqUri):
            conn_url=reqUri.split(':')
            # Port is specified
            conn_port = conn_url[1]
            if ('/' in conn_port):
                conn_port = conn_port.split('/')[0]
        else:
            conn_port = '80'

        print('**************\n\nconn_port:' + conn_port)
        try:
            subprocess.check_output(runscript, stderr=subprocess.STDOUT, shell=True)
            connect_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Allows reuse of Socket Address
            connect_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            connect_sock.settimeout(0.30)
            if('/' in reqUri):
                resource= reqUri.split('/')[1]
                reqUri = reqUri.split('/')[0]
            else:
                resource='/'


            print('**************\n\nreqUri:' + reqUri)
            print('**************\n\nresource:' + resource)
            # Binds Socket
            connect_sock.connect((reqUri,int(conn_port)))
            connect_sock.send(bytes("GET "+ resource +" HTTP/1.1\r\n\r\n",'UTF-8'))
            body = connect_sock.recv(1024).decode()
            connect_sock.close()
            statusCode = '200'
        except (OSError,):
            print("Exception Caught")
            connect_sock.close()
            statusCode = '401'
    else:
        statusCode='400'

    # Process Headers

    if(DEBUG):
        print("RUN SCRIPT\n\n%s\n\n" % str(runscript))

    return(statusCode,body,headers)

def processRequest(clientRequest):
    # Star spliting reuest
    headers=''
    reqBody=''
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
    if(uri != '*' or uri.startswith('\\')):
        fullFilePath = os.path.abspath(WEBAPP_ROOT + uriparts[0])
    else:
        fullFilePath = uri
    if(method == "POST"):
        reqBody = splitreq[-1]
    if (method == "PUT"):
        try:
            reqBody = clientRequest.split("\r\n\r\n")[1]
            print("REQ BODY:\n%s" % reqBody)
        except:
            print("Cannot split request")
            pass

    (exportHeaderList, userAgent) = getHeaders(clientRequest,method,fullFilePath,uriparts)

    if(DEBUG):
        print(str(splitreq[0]))
        print(str(splitreq))
        print("cgiParserCommand: "+ cgiParser)
        print("CLIENT REQUEST:\n\n" + clientRequest)
        print("POST BODY: "+ str(reqBody))
        print("User Agent: " + userAgent)
        print("Method: "+method)
        print("URI: "+uri)
        print("httpVersion: "+httpVersion)
        print("fullFilePath: "+fullFilePath)
        print("uriparts: "+str(uriparts))
        print("NEW HEADER LIST:\n\n"+str(exportHeaderList))

    # Parse request message
    if (httpVersion not in HTTP_VERSION_SUPPORT): # 505 Check
        statusCode = '505'
    elif (method not in HTTP_METHODS): # 405 Check
        statusCode = '405'
    else:
        (statusCode, body, headers) = processMethod(method, exportHeaderList, fullFilePath, reqBody,cgiParser,uri)

    #If status code of request is not 'OK', then set response body
    if (statusCode != '200'):
        body = "<b>" + statusCode + ": </b>" + RESPONSE_CODES[statusCode]

    # Determine if just headers are sent in the request
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
