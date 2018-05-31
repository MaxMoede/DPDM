import mysql.connector
import csv
import git
import os
import subprocess
import sys
from mysql.connector import Error
from operator import itemgetter
from testClasses import *
from getTags import *

class aFile:
	fileUid = ""
	fileName = ""
	projectUid = ""
	projectName = ""
	version = ""
	rules = []
	totBugs = 0

	def __init__(self, fileName, fileUid, numRules):
		self.fileName = fileName.decode("utf-8")
		self.fileUid = fileUid.decode("utf-8")
		self.rules = list([0] * numRules)

	def __init__(self, fileName, fileUid, numRules, projectUid, projectName, version):
		self.fileName = fileName.decode("utf-8")
		self.fileUid = fileUid.decode("utf-8")
		self.rules = list([0] * numRules)
		self.projectUid = projectUid.decode("utf-8")
		self.projectName = projectName.decode("utf-8")
		self.version = version
		#for section in self.rules:
		#		totBugs += secion


class aProjectRelease:
	listOfFiles = {}
	createdAt = 0
	buildDate = 0
	version = ""
	projectName = ""

	def __init__(self, listOfFiles, version, projectName, createdAt, buildDate):
		self.listOfFiles = dict(listOfFiles)
		self.version = version.decode("utf-8")
		self.projectName = projectName.decode("utf-8")
		self.createdAt = createdAt
		self.buildDate = buildDate


class aBaseProject:
	projectName = ""
	projectUid = ""

	def __init__(self, projArr):
		self.projectName = projArr[1].decode("utf-8")
		self.projectUid = projArr[12].decode("utf-8")


class aRule:
	ruleID = 0
	count = 0

	def __init__(self, ruleArr):
		self.ruleID = ruleArr[2]
		self.count = 0

class aSnapshot:
	createdAt = 0
	buildDate = 0
	version = ""
	componentUid = ""
	snapshotUid = ""

	def __init__(self, snapArray):
		self.version = snapArray[3].decode("utf-8")
		self.createdAt = snapArray[15]
		self.buildDate = snapArray[16]
		self.componentUid = snapArray[22].decode("utf-8")
		self.snapshotUid = snapArray[23].decode("utf-8")

class anIssue:
	idKey = ""
	idNum = 0
	ruleID = 0
	creationDate = 0
	createdAt = 0
	updatedAt = 0
	componentUid = ""
	projectUid = ""

	def __init__(self, issueArray):
		self.idNum = issueArray[0]
		self.idKey = issueArray[1].decode("utf-8")
		self.ruleID = issueArray[2]
		self.createdAt = issueArray[17]
		self.updatedAt = issueArray[18]
		self.creationDate = issueArray[19]
		self.componentUid = issueArray[23].decode("utf-8")
		self.projectUid = issueArray[24].decode("utf-8")



def first(iterable, default=None):
  for item in iterable:
    return item
  return default

def getSnapshots():
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
			fullSnapshots.append(aSnapshot(item))

	return fullSnapshots


def createRulesList():
	ruleIDs = []
	try:
		conn = mysql.connector.connect(host='localhost',
	                                   database='sonar',
	                                   user='sonarUser',
			                           password='happify')
		cursor = conn.cursor()
		cursor.execute("SELECT * FROM rules")
		row = cursor.fetchone()
		ruleIDs.append([int(row[0]), row[1]])
		while row is not None:
			row = cursor.fetchone()
			if row is not None:
				ruleIDs.append([int(row[0]), row[1]])
		cursor.close()

	except Error as someError:
		print(someError)

	finally:
		cursor.close()
		conn.close()
	numRules = len(ruleIDs)

	return ruleIDs, numRules


def createIssueIDList():
	ruleIDs = []
	fullRuleIDs = []
	try:
		conn = mysql.connector.connect(host='localhost',
	                                   database='sonar',
	                                   user='sonarUser',
			                           password='happify')
		cursor = conn.cursor()
		cursor.execute("SELECT * FROM active_rules")

		row = cursor.fetchone()
		ruleIDs.append(row)
		while row is not None:
			row = cursor.fetchone()
			if row is not None:
				ruleIDs.append(row)
	except Error as someError:
		print(someError)

	finally:
		cursor.close()
		conn.close()
	numRules = len(ruleIDs)

	for item in ruleIDs:
		if item is not None:
			fullRuleIDs.append(aRule(item))

	return fullRuleIDs, numRules


def connect():
	issues = []
	fullIssues = []
	projects = []
	try:
		conn = mysql.connector.connect(host='localhost',
	                                   database='sonar',
	                                   user='sonarUser',
			                           password='happify')
		print('Connected to Database')
		cursor = conn.cursor()
		cursor.execute("SELECT * FROM issues")

		row = cursor.fetchone()
		issues.append(row)
		while row is not None:
			row = cursor.fetchone()
			issues.append(row)
		cursor.close()
		
		newCursor = conn.cursor()
		newCursor.execute("SELECT * FROM projects")
		row = newCursor.fetchone()
		projects.append(row)
		while row is not None:
			row = newCursor.fetchone()
			projects.append(row)
		newCursor.close()

	except Error as e:
	    print(e)

	finally:
		cursor.close()
		conn.close()

	for item in issues:
		if item is not None:
			fullIssues.append(anIssue(item))

	return fullIssues,projects


def addCurrentIssues(ruleIDs, currentIssues):
	for item in currentIssues:
		for rule in ruleIDs:
			if item is not None:
				if rule.ruleID == item.ruleID:
					rule.count = rule.count + 1;
	ruleIDs.sort(key=lambda x: x.ruleID)
	return ruleIDs

# Generates new project classes from a list of projects and rules
def createProjects(currentProjects, numRules, snapshots):
	projectClasses = []
	baseProjects = findBaseProjects(currentProjects)
	count = 0
	for item in currentProjects:
		if item is not None:
			fileName = item[1]
			fileID = item[12]
			projectUid = item[13].decode("utf-8")
			projectName = findProjectName(baseProjects, projectUid)
			#for thingy in snapshots:
				#print("componentUid: ", thingy.componentUid)
			#print("projectUid: ", projectUid)
			relevantSnapshots = [x for x in snapshots if x.componentUid == projectUid]
			for rSnap in relevantSnapshots:
				#print("ran bitch!!!! version:", rSnap.version)
				newProject = aFile(fileName, fileID, numRules, projectUid, projectName, rSnap.version)
				projectClasses.append(newProject)
				count += 1
	#print(count)

	return projectClasses


#projectClasses are all files in projects file of sql.
### each project class has a project id, project name,
### and list of rules that have been broken. list filled with 0s.
#currentIssues are all things in issues file of sql. 
#ruleIDs are the list of rules from active_rules of sql.
#creates project dict:
### each project in dict has project id as key

def buildProjDict(projectClasses, currentIssues, ruleIDs, snapshots, baseProjects):
	allProjects = {}
	projDict = {}
	projectReleases = []
	snapShotIssues = {}

	#for item in snapshots:
		#print("snapshot:", item)
	for item in baseProjects:
		allProjects[item.projectUid] = {}
		relevantSnapshots = [x for x in snapshots if x.componentUid == item.projectUid]
		for eachSnap in relevantSnapshots:
			#print("individual snapshot:", eachSnap.componentUid, eachSnap.version)
			#print("snap id:", eachSnap.componentUid, projectClasses[0].projectUid)
			#print("Length of projectClasses: ", len(projectClasses))
			newFilesDict = dict((x.fileUid, x) for x in projectClasses if x.version.decode("utf-8") == eachSnap.version.decode("utf-8"))#if x.projectUid == eachSnap.componentUid)
			#print("Length of newFilesDict: ", len(newFilesDict))
			tempFilesDict = newFilesDict.copy()
			newProjectRelease = aProjectRelease(tempFilesDict, eachSnap.version, item.projectName, eachSnap.createdAt, eachSnap.buildDate)
			allProjects[item.projectUid][eachSnap.version] = newProjectRelease
			#print("dict length:", len(allProjects[item.projectUid]))

	return allProjects		

#class anIssue:
#	idKey = ""
#	idNum = 0
#	ruleID = 0
#	creationDate = 0
#	createdAt = 0
#	updatedAt = 0
#	componentUid = ""
#	projectUid = ""

#class aProjectRelease:
#	listOfFiles = {}
#	version = ""
#	projectName = ""
def createTable(ruleCounts, projDict, baseProjects):
	ruleIDCounts = []
	projectRSets = []
	fileKeys = []
	fileRules = []
	count = 0
	for item in ruleCounts:
		ruleIDCounts.append(item.count)

	for baseProjectKey, baseProject in projDict.items():
		for releaseKey, eachRelease in baseProject.items():
			#print("this is a release: ", eachRelease.version)
			#print("length of files list: ", len(eachRelease.listOfFiles))
			eachRelease.listOfFiles = eachRelease.listOfFiles.copy()
	for baseProjectKey, baseProject in projDict.items():
		#print("found baseProject", baseProject)
		for releaseKey, eachRelease in baseProject.items():
			#print("this is a release: ", eachRelease.version)
			#print("length of files list: ", len(eachRelease.listOfFiles))
			for fileKey, eachFile in eachRelease.listOfFiles.items():
				count += 1
				#print("fileKey: ", fileKey)
				if id(eachFile) not in fileRules:
					fileRules.append(id(eachFile))
				else:
					eachFile = aFile(eachFile.fileName, eachFile.fileUid, len(eachFile.rules), eachFile.projectUid, eachFile.projectName, eachFile.version)
					#print("found the same id...")

				if ".java" in eachFile.fileName:
					totalBugsArr = []
					totalBugsArr.insert(0, eachFile.fileName)
					totalBugsArr.insert(0, eachRelease.version)
					totalBugsArr.insert(0, eachRelease.projectName)
					totalBugsArr.append(eachFile.totBugs)
					projectRSets.append(totalBugsArr)
					#eachFile.rules.insert(0, eachFile.fileName)
					#eachFile.rules.insert(0, eachRelease.version)#eachRelease.version)
					#eachFile.rules.insert(0, eachRelease.projectName)
					#eachFile.rules.append(eachFile.totBugs)
					#projectRSets.append(eachFile.rules)
			#print("total count:", count)
	projectRSets.sort(key=lambda x: (x[0], x[1]))
	with open("RefactorTest.csv", "a") as csv_file:
		wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
		for x in range(0, len(projectRSets)):
			wr.writerow(projectRSets[x])



def matchUpIssues(projectClasses, currentIssues, ruleIDs, snapshots, baseProjects):
	allProjects = buildProjDict(projectClasses, currentIssues, ruleIDs, snapshots, baseProjects)
	projDict = {}
	projectReleases = []
	snapShotIssues = {}
	onesToPutIn = []


	for item in currentIssues:
		baseProjID = item.projectUid
		baseProjectDict = allProjects[baseProjID]
		timeKeys = []
		releaseDict = None
		for key, projRelease in baseProjectDict.items():
			if releaseDict is None and projRelease.createdAt < item.createdAt:
				releaseDict = (key, projRelease)
			elif projRelease.createdAt < item.createdAt and releaseDict is not None and projRelease.createdAt > releaseDict[1].createdAt:
				#print("what is projDict[1]: ", releaseDict[1])
				releaseDict = (key, projRelease)
		theFileToAdd = baseProjectDict[releaseDict[0]].listOfFiles[item.componentUid]
		theProjectSelected = baseProjectDict[releaseDict[0]]
		ruleIndexID = first(x for x in ruleIDs if x.ruleID == item.ruleID) 
		toIndex = ruleIDs.index(ruleIndexID)
		theFileToAdd.rules[toIndex] += 1
		theFileToAdd.totBugs += 1
		#print(theFileToAdd.fileName, " total bugs ", theFileToAdd.totBugs)


	return allProjects


def createInitialTable(ruleList):
	ruleStrings = []
	for item in ruleList:
		fullString = "Rule " + str(item.ruleID)
		ruleStrings.append(fullString)
	ruleStrings.insert(0, "Filename")
	ruleStrings.insert(0, "Release #")
	ruleStrings.insert(0, "Project ID")
	ruleStrings.append("Total Bugs")
	with open("RefactorTest.csv", "wb") as csv_file:
		wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
		wr.writerow(ruleStrings)

#SPREADSHEET SETUP:
# PROJ ID || RELEASE # || FILENAME || RULE 1 || RULE 2 || ETC
# THINGS TO DO: 
# Pull release numbers
# get only java filenames
def findProjectName(baseProjects, projectUid):
	for item in baseProjects:
		if item is None:
			baseProjects.remove(item)
	for item in baseProjects:
		if item.projectUid == projectUid.decode("utf-8"):
			return item.projectName
	return "none"


def findBaseProjects(listOfProjects):
	baseProjects = []
	for item in listOfProjects:
		if item is not None:
			if item[12] == item[13]:
				baseProjects.append(aBaseProject(item))
	return baseProjects
       


def runOneProject(projectName):
	ruleIDs, numRules = createIssueIDList()
	currentIssues, currentProjects = connect()
	snapshots = getSnapshots()
	for item in currentProjects:
		if item is None:
			currentProjects.remove(item)
	baseProjects = findBaseProjects(currentProjects)
	ruleCounts = addCurrentIssues(ruleIDs, currentIssues)
	projectClasses = createProjects(currentProjects, numRules, snapshots)
	#initialProjDict = buildProjDict(projectClasses, currentIssues, ruleIDs, snapshots, baseProjects)
	projDict = matchUpIssues(projectClasses, currentIssues, ruleIDs, snapshots, baseProjects)
	#print("snapshot info: ", snapshots[1].version)
	createInitialTable(ruleCounts)
	createTable(ruleCounts, projDict, baseProjects) #use to update big spreadsheet



def main():
	testIssueClass()
	runOneProject("Test")
	#getTags(sys.argv[1])


if __name__ == '__main__':
    main()




