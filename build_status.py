#!/usr/bin/python3.7

try:
	buildstatus = open("build.status", "r")
except FileNotFoundError:
	print("Build status file missing or unreadable.")
	exit(1)
	
status = buildstatus.read().split("\n", 1)

if status[1] == "success":
	exit(0)

else:
	print("BUILD FAILED!")
	print(status[2])
	exit(1)


