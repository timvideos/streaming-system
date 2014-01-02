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
set -e

# Add the users needed
adduser --system website --ingroup website
adduser --system website-run --ingroup website-run
adduser website website-run

# Add current user to the new groups
adduser $USER website
adduser $USER website-run

# Set up the website directory
BASEDIR=/home/website
STATICDIR=/var/www/timvideos-static/
rm -r /tmp/timvideos-static || true

if [ ! -f ~website/.gitconfig ]; then

   cat > ~website/.gitconfig <<EOF
[user]
	email = deployed@mithis.com
	name = `hostname`
EOF
fi

(
if [ ! -d $BASEDIR/timvideos ]; then
	as_website "cd $BASEDIR; git clone git://github.com/timvideos/streaming-system.git timvideos"
else
	chown website:website -R $BASEDIR/timvideos
	as_website "cd $BASEDIR/timvideos; git pull" || exit
fi
cd $BASEDIR

# Update the repository
cd timvideos
as_website git submodule init
as_website git submodule update
as_website chmod -R g+r .
(cd website && as_website make prepare-serve)
export VERSION=$(git describe --tags --long)-$(date +%Y%m%d-%H%M%S)
cd ..

# Version the code
as_website cp -arf timvideos timvideos-$VERSION
as_website rm current || true
as_website ln -s timvideos-$VERSION current

# Directory for the static stuff
mkdir /var/www/timvideos-static || true
chown website:website /var/www/timvideos-static

# Version the static files
cp -R /tmp/timvideos-static $STATICDIR/$VERSION
as_website rm $STATICDIR/current || true
as_website ln -s $STATICDIR/$VERSION $STATICDIR/current

# Need to get config-private.json
# Need to get settings-private.py

# Add the init script
cp $BASEDIR/timvideos-$VERSION/website/conf/init.conf /etc/init/website.conf
ln -sf /lib/init/upstart-job /etc/init.d/website
service website restart

# Add the ngnix config
apt-get install nginx
cp $BASEDIR/timvideos-$VERSION/website/conf/nginx.conf /etc/nginx/sites-available/website-$VERSION
ln -sf /etc/nginx/sites-available/website-$VERSION /etc/nginx/sites-enabled/website
service nginx restart
)
