#!/bin/bash
apt update > /dev/null
apt install netcat-traditional > /dev/null
RESPONSE=$(echo "Hello World!" | nc server 12345 -w 2)
echo $RESPONSE
if [ "$RESPONSE" = "Hello World!" ];
then
    echo "action: test_echo_server | result: success"
else
    echo "action: test_echo_server | result: fail"
fi