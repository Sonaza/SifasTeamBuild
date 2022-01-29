#!/usr/bin/python3.7

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import json
from datetime import datetime, timezone

try:
	status_file = open("build.status", "r+")
except FileNotFoundError:
	print("Build status file missing or unreadable.")
	exit(-1337)

try:
	status = json.load(status_file)
except json.decoder.JSONDecodeError:
	print("Build status file corrupted/not valid json.")
	exit(-1337)
	
timestamp = datetime.fromisoformat(status['timestamp'])

already_handled = False
if status['handled'] != None:
	already_handled = True

status['handled'] = datetime.now(timezone.utc).isoformat()

print()

if status['success'] == True:
	print("-------------- BUILD SUCCESSFUL! --------------")
else:
	print("---------------- BUILD FAILED! ----------------")

print(f"Build date       : {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Automatic        : {status['auto']}")
print(f"Forced           : {status['forced']}")
print()
print(status['message'])

if not already_handled:
	status_file.seek(0)
	status_file.truncate()
	json.dump(status, status_file)
	status_file.close()

if status['success'] == True: # or already_handled or not status['auto']:
	exit(0)

else:
	exit(1)
