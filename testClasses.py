import mysql.connector
import csv
from mysql.connector import Error
from operator import itemgetter
from connectSQL import *


def createActiveRuleSpreadsheet():
	activeRules, numActRules = createIssueIDList()
	allRules, numAllRules = createRulesList()
	activeRuleIDs = []
	activeRuleDescriptions = []
	activeRuleIDs.append("rule id:")
	activeRuleDescriptions.append("description:")
	for ruleTuple in allRules:
		ruleid = ruleTuple[0]
		ruleDescription = ruleTuple[1]
		result = [item for item in activeRules if item[0] == ruleid]
		if len(result) is not 0:
			print("found", ruleid, ruleDescription.decode("utf-8"))
			activeRuleIDs.append(ruleid)
			activeRuleDescriptions.append(ruleDescription.decode("utf-8"))
	with open("ruleDescriptions.csv", "wb") as csv_file:
		wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
		wr.writerow(activeRuleIDs)
		wr.writerow(activeRuleDescriptions)


def testIssueClass():
	issues = []
	issueClasses = []
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
	except Error as e:
	    print(e)

	finally:
		cursor.close()
		conn.close()
	for item in issues:
		if item is not None:
			issueClasses.append(anIssue(item))
	print(issueClasses[3].componentUid)
	print(issueClasses[3].createdAt)


#projectClasses are all files in projects file of sql.
#currentIssues are all things in issues file of sql. 
#ruleIDs are the list of rules from active_rules of sql.
#item[23] is component uid. 
#item[24] is project uid.
def printTotalIssues(projectClasses, currentIssues, ruleIDs, fileUids):
	ruleCount = 0 
	for item in currentIssues:
		if item is not None:
			projUid = item.projectUid
			for thing in fileUids:
				if projUid == thing[1]:
					thing[2] = thing[2] + 1
	for things in fileUids:
		print((things[0]), (things[2]))


def getfileUids(currentProjects):
	fileUids = []
	for item in currentProjects:
		if item is not None:
			componentUid = item[12]
			fileUid = item[13]
			if componentUid == fileUid:
				fileUids.append([item[1], fileUid, 0])
	return fileUids


def getVersionTuples():
	versions = []
	try:
		conn = mysql.connector.connect(host='localhost',
	                                   database='sonar',
	                                   user='sonarUser',
			                           password='happify')
		print('Connected to Database')
		cursor = conn.cursor()
		cursor.execute("SELECT * FROM snapshots")

		row = cursor.fetchone()
		versions.append(row)
		while row is not None:
			row = cursor.fetchone()
			versions.append(row)
		cursor.close()
	except Error as e:
	    print(e)

	finally:
		cursor.close()
		conn.close()
	return versions