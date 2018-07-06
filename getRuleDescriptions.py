import mysql.connector
import csv
import git
import os
import subprocess
import sys
import time
from mysql.connector import Error
from operator import itemgetter


def get_issues():
	issues = []
	fullIssues = []
	projects = []
	time.sleep(30)
	try:
		conn = mysql.connector.connect(host='localhost',
	                                   database='sonar',
	                                   user='sonarUser',
			                           password='happify')
		cursor = conn.cursor()
		cursor.execute("""SELECT R.plugin_rule_key, R.name, A.failure_level, R.system_tags, R.def_remediation_base_effort
							FROM rules R, active_rules A
							WHERE R.language LIKE '%java%' AND
							R.id=A.rule_id""") #used to be R.id as the first thing to grab.
		row = cursor.fetchone()
		issues.append(row)
		while row is not None:
			row = cursor.fetchone()
			#row = row.translate(None, '(),')
			issues.append(row)
		cursor.close()
		
		'''newCursor = conn.cursor()
		newCursor.execute("TRUNCATE issues;")
		newCursor.execute("TRUNCATE projects;")
		newCursor.execute("TRUNCATE snapshots;")
		newCursor.execute("TRUNCATE project_measures;")
		newCursor.execute("TRUNCATE project_links;")
		newCursor.execute("TRUNCATE project_branches;")
		newCursor.execute("TRUNCATE issue_changes;")
		newCursor.execute("TRUNCATE file_sources;")
		newCursor.execute("TRUNCATE events;")
		newCursor.execute("TRUNCATE ce_activity;")
		newCursor.close()'''

	except Error as e:
	    print(e)

	finally:
		cursor.close()
		conn.close()

			
	return issues


def convertToFile(issueList):
	issueList.sort()
	print("hi")
	#index:
	#0: long name
	#1: rule id
	#2: kee
	#3: severity
	#4: tags
	ruleIDs = []
	ruleDescriptions = []
	ruleSeverities = []
	ruleTags = []
	ruleTimes = []
	ruleIDs.append("Rule ID")
	ruleDescriptions.append("Description")
	ruleSeverities.append("Severity")
	ruleTags.append("Tags")
	ruleTimes.append("Time")
	for x in range(0, len(issueList)):
		if issueList[x] is not None:
			ruleIDs.append(issueList[x][0])
			ruleDescriptions.append(issueList[x][1])
			ruleTags.append(issueList[x][3])
			ruleTimes.append(issueList[x][4])
			if issueList[x][2] == 0:
				ruleSeverities.append("INFO")
			elif issueList[x][2] == 1:
				ruleSeverities.append("MINOR")
			elif issueList[x][2] == 2:
				ruleSeverities.append("MAJOR")
			elif issueList[x][2] == 3:
				ruleSeverities.append("CRITICAL")
			elif issueList[x][2] == 4:
				ruleSeverities.append("BLOCKER")
			else:
				ruleSeverities.append("UNKNOWN")
	'''for x in range(0, len(issueList)):
		if issueList[x] is not None:
			ruleDescriptions.append(issueList[x][1])
	for x in range(0, len(issueList)):
		if issueList[x] is not None:
			if issueList[x][2] == 0:
				ruleSeverities.append("INFO")
			elif issueList[x][2] == 1:
				ruleSeverities.append("MINOR")
			elif issueList[x][2] == 2:
				ruleSeverities.append("MAJOR")
			elif issueList[x][2] == 3:
				ruleSeverities.append("CRITICAL")
			elif issueList[x][2] == 4:
				ruleSeverities.append("BLOCKER")
			else:
				ruleSeverities.append("UNKNOWN")
	for x in range(0, len(issueList)):
		if issueList[x] is not None:
			ruleTags.append(issueList[x][3])'''
	with open("ruleDescriptionTable.csv", "wb") as csv_file:
		wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
		wr.writerow(ruleIDs)
		wr.writerow(ruleDescriptions)
		wr.writerow(ruleSeverities)
		wr.writerow(ruleTags)
		wr.writerow(ruleTimes)
	

def main():
	issues = get_issues()
	print("number of issues: {}".format(len(issues)))
	convertToFile(issues)

if __name__ == '__main__':
	main()