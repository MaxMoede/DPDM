import mysql.connector
import csv
import git
import os
import subprocess
import sys
import time
from mysql.connector import Error
from operator import itemgetter

def get_rule_IDs():
	issueIDs = []
	cleanedIssueIDs = []
	try:
		conn = mysql.connector.connect(host='localhost',
	                                   database='sonar',
	                                   user='sonarUser',
			                           password='happify')
		cursor = conn.cursor()
		cursor.execute("""SELECT R.id
							FROM rules R, active_rules A
							WHERE R.language LIKE '%java%' AND
							R.id=A.rule_id""")
		row = cursor.fetchone()
		issueIDs.append(row)
		while row is not None:
			row = cursor.fetchone()
			if row is not None:
				issueIDs.append(row)
		cursor.close()

	except Error as e:
		print(e)

	finally:
		cursor.close()
		conn.close()

	print("number of issue IDs: {}".format(len(issueIDs)))
	for eachIssueID in issueIDs:
		cleanedIssueIDs.append(eachIssueID[0])
	return cleanedIssueIDs

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
		cursor.execute("SELECT DISTINCT P.long_name, I.rule_id, I.kee FROM projects P left join issues I on (P.uuid = I.component_uuid) WHERE P.uuid = I.component_uuid;")

		row = cursor.fetchone()
		issues.append(row)
		while row is not None:
			row = cursor.fetchone()
			issues.append(row)
		cursor.close()
		
		newCursor = conn.cursor()
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
		newCursor.close()

	except Error as e:
	    print(e)

	finally:
		cursor.close()
		conn.close()

			
	return issues

	

def main():
	#issues = get_issues()
	issueIDs = get_rule_IDs()
	#print("number of issues: {}".format(len(issues)))

if __name__ == '__main__':
	main()