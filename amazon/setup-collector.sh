#!/bin/sh

cd ~tansell/

apt-get install vim vim-gnome htop

###############################################################################
# Install our custom version of flumotion
###############################################################################
apt-get install -y git

if [ ! -d timsvideo ]; then
	git clone git://github.com/mithro/timsvideo.git
else
	(
		cd timsvideo
		git pull
	)
fi
(
	cd timsvideo
	git submodule init
	git submodule update
)

# Dependencies to build stuff
apt-get install -y build-essential python-dev autoconf libtool subversion

# Install the core flumotion
(
	cd timsvideo/amazon/flumotion
	./autogen.sh
	make -j16
	make install
)

# Install the ugly plugins
(
	cd timsvideo/amazon/flumotion-ugly
	./autogen.sh
	make -j16
	make install
)

# Dependencies to run flumotion
apt-get install -y python-kiwi

# Copy the config files to /etc
cp -rf timsvideo/amazon/flumotion-config/fromdeb/etc/* /usr/local/etc/
ln -s /usr/local/etc/init.d/flumotion /etc/init.d/flumotion

# Add a flumotion user
adduser --system flumotion --group --home /tmp --no-create-home

###############################################################################
# Get the latest gstreamer we need.
###############################################################################
rm /etc/apt/apt.conf.d/02cache

if [ ! -e /etc/apt/sources.list.d/gstreamer-developers-ppa-lucid.list ]; then
	apt-add-repository ppa:gstreamer-developers/ppa
fi

if grep "gstreamer" /etc/apt/preferences; then
	echo "gstreamer pinned."
else
	cat >> /etc/apt/preferences <<EOF
Explanation: Give the gstreamer PPA higher priority than anything else
Package: *
Pin: release o=LP-PPA-gstreamer-developers
Pin-Priority: 2000
EOF
	apt-cache policy gstreamer-tools 
fi

apt-get update
apt-get install -y gstreamer0.10.* python-gst0.10 gstreamer-tools
apt-get upgrade

rm /etc/apt/sources.list.d/gstreamer-developers-ppa-lucid.list

###############################################################################
# Give access to the firewire ports
###############################################################################
chmod a+rw /dev/raw1394
