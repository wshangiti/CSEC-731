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

def getHeaders(http_req,reqMethod,fullFilePath,uriparts):

    splitreq = http_req.split("\n")
    headerlist = []
    headernum = 0

    while splitreq[headernum] != "\r":
        headerparts = splitreq[headernum].split(": ")
        for hmap in HTTP_BASH_MAP:
            if(hmap[0] == headerparts[0]):
                headerparts[1]=(headerparts[1].strip('\r')).strip()
                headerlist.append(([hmap[1],headerparts[1]]))
        headernum += 1
    headerlist += DEFAULT_EXPORTS
    if(len(uriparts) > 1):
        headerlist.append((['QUERY_STRING', uriparts[1]]))
    headerlist.append((['SCRIPT_FILENAME',fullFilePath]))
    headerlist.append((['REQUEST_METHOD', reqMethod]))

    #print(headerlist)
    return headerlist

def getCGIHeaders(http_req):
    print("CGIHEADER REUESTS:\n\n"+ http_req)
    splitreq = http_req.split("\n")
    headerlist = []
    headernum = 0
    while headernum < len(splitreq):
        headerparts = splitreq[headernum].split(": ")
        for hmap in HTTP_BASH_MAP:
            if (hmap[0] == headerparts[0]):
                headerparts[1] = (headerparts[1].strip('\r')).strip()
                headerlist.append(([hmap[1], headerparts[1]]))
        headernum += 1
    for he in headerlist:
        if(he[0] == 'HTTP_COOKIE'):
            headerlist.append((['SET_COOKIES','TRUE']))
    #print(headerlist)
    return headerlist

def getVars(uri):
    uriparts =uri.split('?')
    # if request is to root of directory use default Root Page
    if(uriparts[0] == '/'):
        uriparts[0] = uriparts[0]+DEFAULT_ROOT_PAGE
    return uriparts

def log_request():
    time_stamp = datetime.datetime.now().strftime("%Y-%m-%d::%H:%M")

def processMethod(reqMethod,exportHeaderList,fullFilePath):
    if(reqMethod == 'GET'):
        print("REACHED: GET")
        executeMethod = "php-cgi -f %s" % (fullFilePath)

        runscript=''
        for hmap in exportHeaderList:
            print("export %s='%s'; " % (hmap[0], hmap[1]))
            runscript += "export %s='%s'; " % (hmap[0], hmap[1])
        runscript += executeMethod
        try:
            body = str(subprocess.check_output(runscript,stderr=subprocess.STDOUT,shell=True))
            print("ORIGBODY: \n\n"+body)
            body = body.strip('^b"').split("\r\n\r\n")
            #print(body)
            moreHeaderList = getCGIHeaders(body[0])
            extrarunscript = ''
            for hmap in moreHeaderList:
                print("export %s='%s'; " % (hmap[0], hmap[1]))
                extrarunscript += "export %s='%s'; " % (hmap[0], hmap[1])
            print(extrarunscript)
            body2 = subprocess.check_output(extrarunscript,stderr=subprocess.STDOUT,shell=True)
            body = str(body[1].replace("\n",""))
            #print(body2)
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
    #print(splitreq)
    return splitreq[1].split(" ")[1]

def processRequest(clientRequest):
    print("CLIENT REQUEST:\n\n"+clientRequest)
    splitreq = clientRequest.split("\n")
    method = str(splitreq[0].split(" ")[0]).strip()
    uri = str(splitreq[0].split(" ")[1]).strip()
    httpVersion = str(splitreq[0].split(" ")[2]).strip()
    uriparts = getVars(uri)
    fullFilePath = os.path.abspath(WEBAPP_ROOT + uriparts[0])

    print("Method: "+method)
    print("URI: "+uri)
    print("httpVersion: "+httpVersion)
    print("fullFilePath: "+fullFilePath)
    print("uriparts: "+str(uriparts))
    exportHeaderList = getHeaders(clientRequest,method,fullFilePath,uriparts)
    print("NEW HEADER LIST:\n\n"+str(exportHeaderList))
    return processResponse(method,uriparts,httpVersion,exportHeaderList,fullFilePath)

def processResponse(method,uriparts,httpVersion,exportHeaderList,fullFilePath):
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
