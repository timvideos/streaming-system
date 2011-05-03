#!/bin/sh

if [ x$1 == xft ]; then
	rm -rf ~/.rvm
	curl -s https://rvm.beginrescueend.com/install/rvm | bash
	sudo apt-get install zlib1g-dev libssl-dev
	rvm install 1.9.2
fi
rvm use 1.9.2
gem install bundle
bundle install
