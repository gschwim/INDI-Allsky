#!/bin/sh

# install the flask server

sudo useradd --shell=/bin/false --no-create-home allsky
sudo mkdir -p /opt/allsky
sudo chown -R allsky:allsky /opt/allsky

# install the indiserver
sudo cp ./systemd/allsky_indiserver.service /etc/systemd/system/
sudo chmod 755 /etc/systemd/system/allsky_indiserver.service


# install the indiclient
sudo cp -a ./indiclient /opt/allsky/
sudo cp ./systemd/allsky_indiclient.service /etc/systemd/system/
sudo chmod 755 /etc/systemd/system/allsky_indiclient.service

# install the webserver
sudo cp -a ./flask /opt/allsky/
sudo cp ./systemd/allsky_web.service /etc/systemd/system
sudo chmod 755 /etc/systemd/system/allsky_web.service


# start it all up

sudo systemctl daemon-reload
sudo systemctl enable allsky_indiserver.service
sudo systemctl start allsky_indiserver.service
sudo systemctl enable allsky_indiclient.service
sudo systemctl start allsky_indiclient.service
sudo systemctl enable allsky_web.service
sudo systemctl start allsky_web.service

systemctl status allsky_indiserver
systemctl status allsky_indiclient
systemctl status allsky_web

