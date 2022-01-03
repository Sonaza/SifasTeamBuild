#!/bin/bash
cd /var/www/sonaza.com/sifas-cards.subdomain

now=$(date)
echo "----------------------------------" >> update.log
echo "Update log for $now" >> update.log
unbuffer -p python3 CardRotations.py $@ | tee -a update.log
