#! /bin/sh

set -x

# Add the users needed
adduser --system website --ingroup website
adduser --system website-run --ingroup website-run
adduser website website-run

# Add current user to the new groups
adduser $USER website
adduser $USER website-run

# Set up the website directory
su website -c "git clone git://github.com/timsvideo/timsvideo.git ~/timsvideo"
su website -c "ln -s ~/timsvideo ~/current"
# Need to get config-private.json

# Add the init script
cp init.conf /etc/init/website.conf
ln -s /lib/init/upstart-job /etc/init.d/website
service website restart

# Add the ngnix config
apt-get install nginx
cp nginx.conf /etc/nginx/sites-available/website
ln -s /etc/nginx/sites-available/website /etc/nginx/sites-enabled/website
service nginx restart
