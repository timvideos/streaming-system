#!/bin/sh

cd ~tansell/

apt-get install vim vim-gnome htop

###############################################################################

rm /etc/apt/sources.list.d/*.save # Remove .save files as they are normally duplicates
rm /etc/apt/apt.conf.d/02cache

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

# Add a flumotion user
adduser --system --quiet --home /usr/local/var/run/flumotion \
	--shell /usr/sbin/nologin --no-create-home --group \
	--disabled-password --disabled-login \
	--gecos "Flumotion Streaming Server" flumotion

# Copy the config files to /etc
cp -rf timsvideo/amazon/flumotion-config/fromdeb/etc/* /usr/local/etc/
ln -s /usr/local/etc/init.d/flumotion /etc/init.d/flumotion

make-ssl-cert /usr/share/ssl-cert/ssleay.cnf /usr/local/etc/flumotion/default.pem
chown flumotion:flumotion /usr/local/etc/flumotion/default.pem

###############################################################################
# Get the latest gstreamer we need.
###############################################################################

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
	if [ -d /etc/apt/preferences.d ]; then
		cat >> /etc/apt/preferences.d/gstreamer-developers-ppa-lucid <<EOF
Explanation: Give the gstreamer PPA higher priority than anything else
Package: *
Pin: release o=LP-PPA-gstreamer-developers
Pin-Priority: 2000
EOF
	fi

fi

apt-cache policy gstreamer-tools 
apt-get update
apt-get install -y gstreamer0.10.* python-gst0.10 gstreamer-tools
apt-get upgrade

rm /etc/apt/sources.list.d/gstreamer-developers-ppa-lucid.list

###############################################################################
# Get the latest vlc so we can stream to justin.tv
###############################################################################

if [ ! -e /etc/apt/sources.list.d/lucid-bleed-ppa-lucid.list ]; then
	add-apt-repository ppa:lucid-bleed/ppa
fi

if grep "lucid-bleed" /etc/apt/preferences; then
	echo "vlc pinned."
else
	cat >> /etc/apt/preferences <<EOF
Explanation: Give the vlc PPA higher priority than anything else
Package: *
Pin: release o=LP-PPA-lucid-bleed
Pin-Priority: 2000
EOF
	if [ -d /etc/apt/preferences.d ]; then
		cat >> /etc/apt/preferences.d/lucid-bleed-ppa-lucid <<EOF
Explanation: Give the vlc PPA higher priority than anything else
Package: *
Pin: release o=LP-PPA-lucid-bleed
Pin-Priority: 2000
EOF
	fi

fi

apt-get update
apt-cache policy vlc
apt-get install -y vlc
apt-get upgrade

rm /etc/apt/sources.list.d/lucid-bleed-ppa-lucid.list

###############################################################################
# Give access to the firewire ports
###############################################################################
chmod a+rw /dev/raw1394

###############################################################################
rm /etc/apt/sources.list.d/*ppa* # Remove the ppa files as they cause problem.
