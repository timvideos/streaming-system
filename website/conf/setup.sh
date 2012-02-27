#! /bin/bash

function as_website {
	su website -c "$*"
	return $?
}

if [ x$USER != xroot ]; then
	echo "Must be run as root!"
	exit
fi

set -x

# Add the users needed
adduser --system website --ingroup website
adduser --system website-run --ingroup website-run
adduser website website-run

# Add current user to the new groups
adduser $USER website
adduser $USER website-run

# Set up the website directory
(
if [ -d timsvideo ]; then
	as_website "cd /home/website; git clone git://github.com/timsvideo/timsvideo.git timsvideo"
else
	as_website "cd /home/website/timsvideo; git pull" || exit
fi
cd /home/website/timsvideo
export VERSION=$(git describe --tags --long)-$(date +%Y%m%d-%H%M%S)
as_website cp -arf ../timsvideo ../timsvideo-$VERSION
(cd website && as_website make prepare-serve)
as_website rm /home/website/current
as_website ln -s /home/website/timsvideo-$VERSION /home/website/current
as_website chmod -R g+w /home/website
# Need to get config-private.json
# Need to get settings-private.py
)

# Add the init script
cp init.conf /etc/init/website.conf
ln -sf /lib/init/upstart-job /etc/init.d/website
service website restart

# Add the ngnix config
apt-get install nginx
cp nginx.conf /etc/nginx/sites-available/website
ln -sf /etc/nginx/sites-available/website /etc/nginx/sites-enabled/website
service nginx restart
