#!/bin/bash
git pull
chown -R sonaza.com:sonaza.com /var/www/sonaza.com/sifas-cards.subdomain
./card_rotation_update.sh
