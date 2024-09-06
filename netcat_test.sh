#!/bin/bash
apt update > /dev/null
apt install netcat-traditional > /dev/null
echo "Hello World!" | nc server 12345 -w 2 > /dev/null
if [ $? -eq 0 ]
then
    echo "action: test_echo_server | result: success"
else
    echo "action: test_echo_server | result: fail"
fi
