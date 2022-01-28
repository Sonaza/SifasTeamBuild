#!/bin/bash
git pull
chown -R sonaza.com:sonaza.com /var/www/sonaza.com/sifas-cards.subdomain
sudo -u sonaza.com -H sh -c "./card_rotation_update.sh"
