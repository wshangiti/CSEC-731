#!/bin/bash
echo 'CONNECT www.rit.edu HTTP/1.1' | nc 127.0.0.1 8080
echo 'DELETE /temp.txt HTTP/1.1' | nc 127.0.0.1 8080
echo 'PUT /temp.txt HTTP/1.1 \r\n\r\n<br>bob' | nc 127.0.0.1 8080