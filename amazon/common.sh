#!/bin/sh

SERVER=$1
TYPE=$2
TYPE=${TYPE:="encoder"}

if [ x$TYPE == encoder ]; then
	COLLECTOR=$3
	if [ x$COLLECTOR == x ]; then
		echo "Must specify the collector to connect this encoder too."
	fi
fi

USER=ubuntu
RUN="ssh $USER@$SERVER"
SUDO="$RUN sudo"
