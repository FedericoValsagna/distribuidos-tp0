#!/bin/bash
docker run --name ping_test -d -p 8080:80 nginx > /dev/null
docker network connect tp0_testing_net ping_test > /dev/null
cat netcat_test.sh | docker container exec -i ping_test bin/sh 2>/dev/null
docker network disconnect tp0_testing_net ping_test > /dev/null
docker stop ping_test > /dev/null
docker container rm ping_test > /dev/null