#!/bin/bash

git pull
if [ "$(whoami)" == "sonaza.com" ]; then
	./card_rotation_update.sh
else
	sudo -u sonaza.com -H sh -c "./card_rotation_update.sh"
fi
