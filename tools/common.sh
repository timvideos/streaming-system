#!/bin/sh

SERVER=$1
TYPE=$2
TYPE=${TYPE:="encoder"}

if [ x$TYPE == xencoder ]; then
	COLLECTOR=$3
	if [ x$COLLECTOR == x ]; then
		echo "Must specify the collector to connect this encoder too."
		exit
	else
		echo "Using a collector of '$COLLECTOR'"
	fi
fi

USER=ubuntu
RUN="ssh $USER@$SERVER"
SUDO="$RUN sudo"
