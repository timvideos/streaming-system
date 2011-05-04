#!/bin/bash

source common.sh

# Setup a connection
ssh $USER@$SERVER true
rm /home/tansell/.ssh/tmp/master-$USER@$SERVER:22
ssh $USER@$SERVER sleep 300 >/dev/null 2>&1 < /dev/null &
SSHPID=$!
echo "Primary SSH connection is $SSHPID"
# Wait for the connection to come up
CONNECTED=254
while [ $CONNECTED -ne 1 ]; do
	sleep 1
	ssh $USER@$SERVER true 2>&1 | grep "ControlSocket" > /dev/null
	CONNECTED=$?
done

$SUDO "apt-get -f install"

# Enable multiverse
$SUDO "cat /etc/apt/sources.list | grep 'universe' | sed -e's/universe/multiverse/' > /tmp/multiverse.list"
$SUDO "mv /tmp/multiverse.list /etc/apt/sources.list.d/multiverse.list"

# Add the required fluendo PPAs
$SUDO "apt-add-repository ppa:flumotion-dev/flumotion"
#$SUDO "apt-add-repository ppa:gstreamer-developers/ppa"

$SUDO "rm /etc/apt/sources.list.d/*.save"

# Update the software
$SUDO "aptitude update"
$SUDO "aptitude full-upgrade -y"

$SUDO "apt-get install -y flumotion flumotion-ugly"

kill $SSHPID
