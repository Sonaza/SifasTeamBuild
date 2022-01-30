#!/bin/bash
export PATH="$PATH:/var/www/sonaza.com/.local/bin/"
set -euo pipefail

cd /var/www/sonaza.com/sifas-cards.subdomain

now=$(date)
echo "Update log for $now"

if [ "$(whoami)" == "sonaza.com" ]; then
	pipenv run python3.7 CardRotations.py $@
else
	./pipenv run python3.7 CardRotations.py $@
fi
