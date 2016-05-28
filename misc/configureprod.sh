#!/bin/bash

set -x
set -e

if [[ $(whoami) != "showthedocs" ]]; then
    echo 'run this script as user showthedocs'
    read -p "create user showthedocs and switch to it? " -r
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo adduser showthedocs
        sudo usermod -aG sudo showthedocs
        echo 'run sudo -i -u showthedocs and rerun this script'
    else
        exit
    fi
fi

sudo apt-get update -y
sudo apt-get upgrade -y

sudo apt-get install -y git make python-pip
sudo apt-get install -y nginx supervisor
sudo apt-get install -y libxml2-dev libxslt1-dev python-dev

sudo pip install --upgrade pip
sudo pip install virtualenv

CLONE=~/repo
git clone https://github.com/idank/showthedocs.git $CLONE
virtualenv env
source env/bin/activate

pip install uwsgi

cd $CLONE
pip install -r requirements.txt

sudo cp misc/supervisor.conf /etc/supervisor/conf.d/uwsgi.conf
sudo cp misc/nginx.conf /etc/nginx/sites-available/showthedocs.conf
cd /etc/nginx/sites-enabled/
sudo rm default || true
sudo ln -s /etc/nginx/sites-available/showthedocs.conf showthedocs

cd
mkdir logs
sudo supervisorctl reload
sudo supervisorctl restart uwsgi
sudo /etc/init.d/nginx reload

echo DONE
