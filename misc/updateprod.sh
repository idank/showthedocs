#!/bin/bash

set -x
set -e

if [[ $(whoami) != "showthedocs" ]]; then
    echo 'run this script as user showthedocs'
    exit 1
fi

cd ~/repo
echo 'pulling main repo'
git pull
cd external
echo 'pulling docs repo'
git pull

echo 'sending uwsgi SIGHUP'
sudo supervisorctl signal HUP uwsgi

echo DONE
