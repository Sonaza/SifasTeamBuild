#!/bin/bash
# export PATH="$PATH:/var/www/sonaza.com/.local/bin/"

RUN_AS_USER="sonaza.com"

if [ "$(whoami)" != $RUN_AS_USER ]; then
	
	echo "$(whoami) is not the correct user. Running script as another user..."
	
	sudo -u $RUN_AS_USER -H sh -c "./build.sh $*"
	exit 0
	
fi

echo "Checking for updates..."

git remote update
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u})
BASE=$(git merge-base @ @{u})

if [ $LOCAL = $REMOTE ]; then
	
	echo "Local repository is already up to date."
	
elif [ $LOCAL = $BASE ]; then
	
	CHANGES=$(git diff --name-only "$LOCAL" "$REMOTE")
	git pull
	
	if [ $? -eq 0 ]; then
		echo "Repository updated."
		if grep -q "\Pipfile.lock$" <<< "$CHANGES"; then
			echo "Pipenv.lock was updated, running pipenv install..."
			pipenv install
	    fi
	    
	    ./build.sh $@
	
	else
	    echo "Repository update failed. Aborting..."
	fi
	
fi

echo "Deploy finished."
