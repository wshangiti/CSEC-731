<?php

$dictionary = array('one' => 'uno', 'two' => 'due', 'three' => 'tre');

if ($_SERVER['REQUEST_METHOD'] == 'OPTIONS') {
    if (isset($_SERVER['HTTP_ACCESS_CONTROL_REQUEST_METHOD']) && $_SERVER['HTTP_ACCESS_CONTROL_REQUEST_METHOD'] == 'POST') {
        header('Access-Control-Allow-Origin: *');
        header('Access-Control-Allow-Headers: X-Requested-With, content-type, access-control-allow-origin, access-control-allow-methods, access-control-allow-headers');
    }
    exit;
}

$json = file_get_contents('php://input');
$obj = json_decode($json);

if (array_key_exists($obj->searchterm, $dictionary)) {
    $response = json_encode(array('result' => 1, 'word' => $dictionary[$obj->searchterm]));
}
else {
    $response = json_encode(array('result' => 0, 'word' => 'Not Found'));
}

header('Content-type: application/json');
header('Access-Control-Allow-Origin: *');
echo $response;

?>