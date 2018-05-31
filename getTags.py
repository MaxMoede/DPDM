import mysql.connector
import csv
import git
import os
import subprocess
import sys
from mysql.connector import Error
from operator import itemgetter
from testClasses import *
from connectSQL import *


def getRanVersions():
	snapshots = []
	fullSnapshots = []
	try:
		conn = mysql.connector.connect(host='localhost',
	                                   database='sonar',
	                                   user='sonarUser',
			                           password='happify')
		cursor = conn.cursor()
		cursor.execute("SELECT * FROM snapshots")
		row = cursor.fetchone()
		snapshots.append(row)
		while row is not None:
			row = cursor.fetchone()
			snapshots.append(row)
		cursor.close()

	except Error as someError:
		print(someError)

	finally:
		cursor.close()
		conn.close()

	for item in snapshots:
		if item is not None:
			fullSnapshots.append(aSnapshot(item).version)

	return fullSnapshots


def getTags(projectPath):
	finalTags = []
	print("current dir: ", os.path.abspath(os.curdir))
	os.chdir(projectPath)
	output = subprocess.check_output("git tag", shell=True)
	newOutput = output.split("\n")
	print("new output: ", newOutput)
	for item in newOutput:
		if "-" not in item:
			if "0." not in item:
				if item not in finalTags:
					finalTags.append(item)

	print(finalTags)

	return finalTags

def getAllTags(projectPath):
	finalTags = []
	fullTags = []
	print("current dir: ", os.path.abspath(os.curdir))
	#os.chdir(projectPath)
	output = subprocess.check_output("git tag", shell=True)
	newOutput = output.split("\n")
	print("new output: ", newOutput)
	for item in newOutput:
		if item not in finalTags:
			finalTags.append(item)
	for thing in finalTags:
			fullDate = subprocess.check_output("git log -1 --format=%ai {}".format(thing), shell=True)
			newDate = fullDate.split(" ")[0]
			fullTags.append((thing, newDate))
		
	return fullTags

def runSonarMaven(newOutput):
	count = 0
	for item in newOutput:
		count = count + 1
		try:
			print("checking out:", item)
			subprocess.check_output("git checkout tags/" + item, shell=True)
			subprocess.check_output("mvn clean install", shell=True)
			subprocess.check_output("mvn sonar:sonar ", shell=True)
		except subprocess.CalledProcessError as someError:
			print(someError)



def main():
	versionsToBeRan = []
	allVersions = getAllTags(sys.argv[1])
	ranVersions = getRanVersions()
	for item in allVersions:
		if str(item) not in ranVersions:
			versionsToBeRan.append(item)
	print(versionsToBeRan)
	for vers in allVersions:
		print("hey", vers)
	#runSonarMaven(versionsToBeRan)
		#print(item.version)


if __name__ == '__main__':
	main()





