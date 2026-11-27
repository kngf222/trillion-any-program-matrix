#!/bin/sh
exec /usr/local/bin/docker run --rm alpine:3 sh -c 'echo "{\"program\":\"docker-alpine\",\"kernel\":\"$(uname -sr)\",\"os\":\"$(. /etc/os-release; echo $PRETTY_NAME)\"}"'
