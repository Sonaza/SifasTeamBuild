#!/bin/bash
# export PATH="$PATH:/var/www/sonaza.com/.local/bin/"

RUN_AS_USER="sonaza.com"

if [ "$(whoami)" != $RUN_AS_USER ]; then
	echo "$(whoami) is not the correct user. Running script as another user..."
	
	exec sudo -u $RUN_AS_USER -H -s bash -c "./deploy.sh $*"
	exit 0
fi

eval "$(ssh-agent -s)" &> /dev/null
ssh-add ~/.ssh/github_ed25519 &> /dev/null

echo
echo "Checking for updates..."
git remote update

if [ $? -ne 0 ]; then
	echo "An error occurred. Deploy has been aborted."
	exit 1
fi

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
			echo "Pipenv.lock was updated, running pipenv sync..."
			pipenv sync
	    fi
	    
	    ./build.sh $@
	
	else
	    echo "Repository update failed. Aborting..."
	fi
	
fi

echo "Deploy finished."
echo

exit 0
