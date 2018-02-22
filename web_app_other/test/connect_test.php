<?php
//https://stackoverflow.com/questions/16934409/curl-as-proxy-deal-with-https-connect-method
class proxy {

    static $server;
    static $client;

    static function headers($str) { // Parses HTTP headers into an array
        $tmp = preg_split("'\r?\n'",$str);
        $output = array();
        $output[] = explode(' ',array_shift($tmp));
        $post = ($output[0][0] == 'POST' ? true : false);

            foreach($tmp as $i => $header) {
                if($post && !trim($header)) {
                    $output['POST'] = $tmp[$i+1];
                    break;
                }
                else {
                    $l = explode(':',$header,2);
                    $output[$l[0]] = $l[0].': '.ltrim($l[1]);
                }
            }
        return $output;
    }

    public function output($curl,$data) {
        socket_write(proxy::$client,$data);
        return strlen($data);
    }
}




$ip = "127.0.0.1";
$port = 50000;

proxy::$server = socket_create(AF_INET,SOCK_STREAM, SOL_TCP);
socket_set_option(proxy::$server,SOL_SOCKET,SO_REUSEADDR,1);
socket_bind(proxy::$server,$ip,50000);
socket_getsockname(proxy::$server,$ip,$port);
socket_listen(proxy::$server);

while(proxy::$client = socket_accept(proxy::$server)) {

    $input = socket_read(proxy::$client,4096);
    preg_match("'^([^\s]+)\s([^\s]+)\s([^\r\n]+)'ims",$input,$request);
    $headers = proxy::headers($input);

        echo $input,"\n\n";
            if(preg_match("'^CONNECT ([^ ]+):(\d+) '",$input,$match)) { // HTTPS
                // fork to allow multiple connections
                if(pcntl_fork())
                    continue;

                $connect_host = $match[1];
                $connect_port = $match[2];

                // connect to endpoint
                $connection = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
                if(!socket_connect($connection, gethostbyname($connect_host), $connect_port))
                    exit;

                // let the client know that we're connected
                socket_write(proxy::$client,"HTTP/1.1 200 Connection Established\r\n\r\n");

                // proxy data
                $all_sockets = array($connection, proxy::$client);
                $null = null;
                while(($sockets = $all_sockets)
                      && false !== socket_select($sockets, $null, $null, 10)
                ) {
                    // can we read from the client without blocking?
                    if(in_array(proxy::$client, $sockets)) {
                        $buf = null;
                        socket_recv(proxy::$client, $buf, 8192, MSG_DONTWAIT);
                        echo "CLIENT => ENDPOINT (" . strlen($buf) . " bytes)\n";
                        if($buf === null)
                            exit;
                        socket_send($connection, $buf, strlen($buf), 0);
                    }

                    // can we read from the endpoint without blocking?
                    if(in_array($connection, $sockets)) {
                        $buf = null;
                        socket_recv($connection, $buf, 8192, MSG_DONTWAIT);
                        echo "ENDPOINT => CLIENT (" . strlen($buf) . " bytes)\n";
                        if($buf === null)
                            exit;
                        socket_send(proxy::$client, $buf, strlen($buf), 0);
                    }
                }

                exit;
            }
            else { // HTTP

                        $input = preg_replace("'^([^\s]+)\s([a-z]+://)?[a-z0-9\.\-]+'","\\1 ",$input);
                        $curl = curl_init($request[2]);
                        curl_setopt($curl,CURLOPT_HEADER,1);
                        curl_setopt($curl,CURLOPT_HTTPHEADER,$headers);
                        curl_setopt($curl,CURLOPT_TIMEOUT,15);
                        curl_setopt($curl,CURLOPT_RETURNTRANSFER,1);
                        curl_setopt($curl,CURLOPT_NOPROGRESS,1);
                        curl_setopt($curl,CURLOPT_VERBOSE,1);
                        curl_setopt($curl,CURLOPT_AUTOREFERER,true);
                        curl_setopt($curl,CURLOPT_FOLLOWLOCATION,1);
                        curl_setopt($curl,CURLOPT_WRITEFUNCTION, array("proxy","output"));
                        curl_exec($curl);
                        curl_close($curl);
            }
    socket_close(proxy::$client);
}
socket_close(proxy::$server);