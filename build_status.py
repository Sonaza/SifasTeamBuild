#!/usr/bin/python3.7

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import json
from datetime import datetime, timezone, timedelta

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
now = datetime.now(timezone.utc)
today = now - timedelta(hours=6, minutes=6)

has_built_today = (timestamp.hour >= 6 and timestamp.day == today.day) or (timestamp.day >= today.day and not status['auto'])

already_handled = False
if status['handled'] != None:
	already_handled = True

status['handled'] = datetime.now(timezone.utc).isoformat()

print()

if not has_built_today:
	print("--------- WARNING! BUILD NOT RUN YET! ---------")
	print("Today's build should have run by now.")
	print()
	
	print("------------------ CRON LOG! ------------------\n")
	try:
		cron_log = open("cron-update.log", "r")
		print(cron_log.read())
	except:
		print("Unable to read cron update log...")
	print("-----------------------------------------------")
	
	print()
	print("Below are the details for most recent build.")
	print()

if status['success'] == True:
	print("-------------- BUILD SUCCESSFUL! --------------")
else:
	print("---------------- BUILD FAILED! ----------------")

print(f"Build date       : {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Automatic        : {status['auto']}")
print(f"Forced           : {status['forced']}")
print()

if not status['success'] and status['auto']:
	print("------------------ CRON LOG! ------------------\n")
	try:
		cron_log = open("cron-update.log", "r")
		print(cron_log.read())
	except:
		print("Unable to read cron update log...")
	print("-----------------------------------------------")
	print()

print(status['message'])

if not already_handled:
	status_file.seek(0)
	status_file.truncate()
	json.dump(status, status_file)
	status_file.close()
	
if not has_built_today:
	exit(2)

elif status['success'] == True or not status['auto']:
	exit(0)

else:
	exit(1)
