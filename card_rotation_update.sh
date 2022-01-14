#!/bin/bash
set -euo pipefail
cd /var/www/sonaza.com/sifas-cards.subdomain

now=$(date)
echo "----------------------------------"
echo "Update log for $now"
python3 CardRotations.py $@
