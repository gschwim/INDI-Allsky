#!/bin/sh

# shut all services
sudo systemctl stop allsky_indiclient
sudo systemctl stop allsky_indiserver
sudo systemctl stop allsky_web
sudo systemctl daemon-reload

# remove the allsky services and directories
sudo rm /etc/systemd/system/allsky_*.service
sudo rm -rf /opt/allsky

# remove the user
sudo userdel allsky

