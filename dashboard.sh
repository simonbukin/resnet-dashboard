#!/bin/bash

xset s noblank
xset s off
xset -dpms

unclutter -idle 0.5 -root &

chromium-browser --incognito --start-maximized --kiosk http://0.0.0.0:5000  &
cd /home/pi/resnet-dashboard
pipenv run python app.py
