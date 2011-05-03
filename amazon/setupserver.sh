#!/bin/sh

SERVER=$1

TYPE=$2
TYPE=${TYPE:="encoder"}

COLLECTOR=$3
if [ x$COLLECTOR == x ]; then
	echo "Must specify the collector to connect this encoder too."
fi

USER=ubuntu
RUN="ssh $USER@$SERVER"
SUDO="$RUN sudo"

echo "Setting up $1 as $TYPE"

# Setup a connection
rm /home/tansell/.ssh/tmp/master-$USER@$SERVER:22
ssh $USER@$SERVER sleep 300 &
SSHPID=$!
echo "Primary SSH connection is $SSHPID"
# Wait for the connection to come up
CONNECTED=254
while [ $CONNECTED -ne 1 ]; do
	sleep 1
	ssh $USER@$SERVER true 2>&1 | grep "ControlSocket" > /dev/null
	CONNECTED=$?
done

# Add multiverse
$SUDO "cat /etc/apt/sources.list | sed -e's/main universe/multiverse/' > /tmp/multiverse.list"
$SUDO "mv /tmp/multiverse.list /etc/apt/sources.list.d/multiverse.list"

# Make sure everything is configured
$SUDO "dpkg --configure -a"

# Clean up any hanging files
$SUDO "apt-get autoremove"

# Update the software
$SUDO "aptitude update"
$SUDO "aptitude full-upgrade -y"

# Install ffmpeg
scp ../debs/ffmpeg/* $USER@$SERVER:/tmp
$SUDO "dpkg --install /tmp/*.deb"
$SUDO "rm /tmp/*.deb"

# Install any deps ffmpeg needs
$SUDO "apt-get install -y libxvidcore4 libvorbisenc2 libtheora0 libopencore-amrwb0 libopencore-amrnb0 libfaac0"
$SUDO "apt-get -f install"

# Copy the ffserver config up
FFSERVERCONF=/tmp/$SERVER.ffserver.conf
cat ffserver/ffserver.conf.$TYPE | sed -e"s/\$COLLECTOR/$COLLECTOR/" > $FFSERVERCONF
scp $FFSERVERCONF $USER@$SERVER:/tmp/ffserver.conf
$SUDO mv /tmp/ffserver.conf /etc/ffserver.conf
rm $FFSERVERCONF

kill $SSHPID
