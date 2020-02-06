#!/bin/sh

# install the flask server

sudo useradd --shell=/bin/false --no-create-home allsky
sudo mkdir -p /opt/allsky
sudo chown -R allsky:allsky /opt/allsky

sudo cp -a ./flask /opt/allsky/

sudo cp ./flask/allsky_web.service /etc/systemd/system
sudo chmod 755 /etc/systemd/system/allsky_web.service

sudo systemctl daemon-reload
sudo systemctl enable allsky_web.service
sudo systemctl start allsky_web.service


# install the indiserver service
sudo cp ./indi/allsky_indiserver.service /etc/systemd/system
sudo chmod 755 /etc/systemd/system/allsky_web.service

sudo systemctl daemon-reload
sudo systemctl enable allsky_indiserver.service
sudo systemctl start allsky_indiserver.service



