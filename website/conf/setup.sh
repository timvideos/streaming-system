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

# Add the groups required
addgroup --system website
addgroup --system website-run

# Add the users needed
adduser --system website --ingroup website --shell /bin/bash --disabled-password --disabled-login
adduser --system website-run --ingroup website-run --shell /bin/false --disabled-password --disabled-login
adduser website website-run

# Add current user to the new groups
adduser $USER website
adduser $USER website-run

# Get python dependencies
apt-get -y install python-pip python-setuptools python-virtualenv

# Set up the website directory
BASEDIR=/home/website

# Set up upstart config file
ln -sf $BASEDIR/current/website/conf/init.conf /etc/init/website.conf
ln -sf /lib/init/upstart-job /etc/init.d/website

# Set up nginx config file
apt-get -y install nginx
ln -sf $BASEDIR/current/website/conf/nginx.conf /etc/nginx/sites-available/website
ln -sf /etc/nginx/sites-available/website /etc/nginx/sites-enabled/website

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
	as_website "cd $BASEDIR/timvideos; git fetch; git reset --hard $(git rev-parse --symbolic-full-name --abbrev-ref @{u})" || exit
fi
cd $BASEDIR

# Update the repository
cd timvideos
as_website git submodule init
as_website git submodule update
as_website chmod -R g+r .
(cd website && as_website make prepare-serve)
export VERSION=$(date +%Y%m%d-%H%M%S)-$(git describe --tags --long --always)
cd ..

if [ ! -f $BASEDIR/timvideos/website/private/settings.py ]; then
  echo "Please create a settings.py file in $BASEDIR/timvideos/website/private/settings.py"
  exit 1
fi

VERSIONDIR=$BASEDIR/timvideos-$VERSION

# Version the code
as_website cp -arf $BASEDIR/timvideos $VERSIONDIR

# Version the static files
cp -R /tmp/timvideos-static $VERSIONDIR/website/static

# Update the current file
as_website rm current || true
as_website ln -s timvideos-$VERSION current

# Need to get config-private.json
# Need to get settings-private.py

# Make upstart/gunicorn reload config file
chmod 644 $VERSIONDIR/website/conf/init.conf
initctl reload-configuration
service website restart

# Make nginx reload config file
chmod 644 $VERSIONDIR/website/conf/nginx.conf
service nginx restart
)
