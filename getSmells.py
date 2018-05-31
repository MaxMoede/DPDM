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
		#print('Connected to Database')
		cursor = conn.cursor()
		cursor.execute("SELECT DISTINCT P.long_name, I.rule_id, I.kee FROM projects P left join issues I on (P.uuid = I.component_uuid) WHERE P.uuid = I.component_uuid;")

		row = cursor.fetchone()
		issues.append(row)
		while row is not None:
			row = cursor.fetchone()
			#print("HEY I GOT SOMETHING! {}".format(row))
			issues.append(row)
		#cursor.execute("DROP DATABASE sonar")
		#cursor.execute("TRUNCATE TABLE issues")
		#cursor.execute("TRUNCATE TABLE projects")
		#cursor.execute("CREATE DATABASE sonar")
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
	issues = get_issues()
	#print("number of issues: {}".format(len(issues)))

if __name__ == '__main__':
	main()