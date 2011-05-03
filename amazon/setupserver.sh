#!/bin/sh

. common.sh

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

. updateconfig.sh

kill $SSHPID $1 $2 $3
