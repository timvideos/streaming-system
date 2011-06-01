#!/bin/bash

rm /etc/apt/sources.list.d/*.save

apt-get install python-software-properties

# Enable multiverse
cat /etc/apt/sources.list | grep 'universe' | sed -e's/universe/multiverse/' > /tmp/multiverse.list
mv /tmp/multiverse.list /etc/apt/sources.list.d/multiverse.list

# Update the software
aptitude update
aptitude full-upgrade -y

apt-get install -y git-core subversion vim bash-completion htop

# Setup the flumotion
# ---------------------------------------------------------------
# Add the required gstreamer PPAs
apt-add-repository ppa:gstreamer-developers/ppa
apt-get update
apt-get install -y gstreamer0.10.* python-gst0.10.*

git clone git://github.com/mithro/timsvideo.git
cd timsvideo
git submodule init
git submodule update

# Packages needed to build
apt-get install build-essential autoconf libtool libxml-parser-perl python-dev libvorbis-dev libogg-dev libtheora-dev libvpx-dev
(
	cd flumotion
	./autogen.sh
	make -j16
	make install
)
(
	cd flumotion-ugly
	./autogen.sh
	make
	make install
)

mkdir -p /usr/local/etc/flumotion
cp -rf flumotion-config/fromdeb/* /usr/local/etc/flumotion
cp flumotion-config/init /etc/init.d/flumotion

# Packages needed to run
apt-get install python-twisted.* ssl-cert


# Setup Streaming to justin.tv
# ---------------------------------------------------------------
add-apt-repository ppa:lucid-bleed/ppa
apt-get update

apt-get install -y vlc.*

git clone git://github.com/justintv/jtvlc.git

# cvlc -vv http://localhost:8081/loop.raw --sout='#rtp{dst=127.0.0.1,port=1234,sdp=file:///tmp/vlc.sdp}' 
# Key found at - http://www.justin.tv/broadcast/adv_other
# python ./jtvlc.py mithro1 live_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX /tmp/vlc.sdp

#kill $SSHPID
