<?php
#echo "<!DOCTYPE html>";

// Generate keys in console:
// Put it in device
// openssl genrsa -out private_key.key 8192
// sudo chown .www-data private_key.key
// sudo chmod g+r private_key.key
// openssl rsa -in private_key.key -out public_key.pem -pubout -outform PEM
// Test data

$ret = session_start();
#echo "Session ret: ", $ret, "<br>";

$_SESSION['favcolor'] = 'green';
$_SESSION['animal']   = 'cat';
$_SESSION['time']     = time();

// Encrypt data with public key
$publicKey = file_get_contents('pub_2048.pem');
if ($publicKey == False)
    {
    echo "No public key.\n";
    exit();
    }
?>


