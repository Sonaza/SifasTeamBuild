#!/usr/bin/python3.7

try:
	buildstatus = open("/var/www/sonaza.com/sifas-cards.subdomain/build.status", "r")
except FileNotFoundError:
	print("Build status file missing or unreadable.")
	exit(-1337)
	
status = [x.strip() for x in buildstatus.read().split("\n", 2)]

if status[1] == "success":
	print("BUILD SUCCESSFUL!")
	exit(0)

elif status[1] == "failed":
	print("BUILD FAILED!")
	print(status[2])
	exit(1)

exit(-1337)
