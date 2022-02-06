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

now = datetime.now(timezone.utc)
disable_built_check = (now.hour == 6 and (now.minute >= 0 and now.minute <= 10)) or (now.hour == 5 and now.minute >= 55)

timestamp = datetime.fromisoformat(status['timestamp'])

timestamp_adjusted = timestamp - timedelta(hours=6, minutes=2)
today_adjusted = now - timedelta(hours=6, minutes=2)

# print()
# print("timestamp", timestamp)
# print("today", today)
# print(timestamp.day, today.day)

has_built_today = (timestamp_adjusted.day == today_adjusted.day)

already_handled = False
if status['handled'] != None:
	already_handled = True

status['handled'] = datetime.now(timezone.utc).isoformat()

print()

if not disable_built_check and not has_built_today:
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
	
if not disable_built_check and not has_built_today:
	exit(2)

elif status['success'] == True or not status['auto']:
	exit(0)

else:
	exit(1)
