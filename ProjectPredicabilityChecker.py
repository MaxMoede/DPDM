#AUTHORS
#TYELER BRIDGES
#TINA RICKARD
#MAX MOEDE
from jira import JIRA
from git import Repo
import tempfile
import json
import time
import csv
import subprocess
import os
import re
import git
import sys
import itertools
from datetime import date, timedelta, datetime
from getTags import *
#Regular expressions to extract date, author, and whether requirement was bug fix or not
DateRegex = r'Date:   [A-Za-z]{3} ([A-Za-z]{3}) ([0-9]{2}) [A-Za-z0-9:]{8} ([0-9]{4})'	
FixRegex = r' (fix) '
AuthorRegex = r'Author: ([A-Za-z ]+)'
initialFolder = ""
bugRegex = r'bug[# \t]*[0-9]+'
prRegex = r'pr[# \t]*[0-9]+'
showBugRegex = r'show\_bug\.cgi\?id=[0-9]+'
bug2Regex = r'\[[0-9]+\]'
tagDates = []
tagTikaDict = {}

#Helper function convert extracted date 
def MonthToNum(shortMonth):

	return{
		'Jan' : 1,
		'Feb' : 2,
		'Mar' : 3,
		'Apr' : 4,
		'May' : 5,
		'Jun' : 6,
		'Jul' : 7,
		'Aug' : 8,
		'Sep' : 9, 
		'Oct': 10,
		'Nov': 11,
		'Dec': 12
	}[shortMonth]

class firstDate:
	creationDate = ""
	def __init__(self, name):
		self.name = name

#Class to go through commits 
class Files:
	classes = []

	def __init__(self):
		self.files = dict()
	#Function updates 
	def updateCommits(self, commits, reqName, start, reqStartDate):
		repoPath = initialFolder + "/" + sys.argv[1]
		repo = Repo(repoPath)
		assert not repo.bare
		print reqName + '\n\n'
		for i in range (0, len(commits)):
			commitobj = repo.commit(commits[i])
			#print("Commit object: {}".format(commitobj))
			self.update(commitobj, reqStartDate)
			self.update_BeginningSize(commitobj, start)
    
	def update(self, commit, reqStartDate):
		stat = commit.stats
		print("current directory: ", os.getcwd())
		print("STAT FILES:", commit.stats.files)
		print("commit number: ", str(commit))
		commitFiles = stat.files
		commitmessage = subprocess.check_output("git log " + str(commit), shell=True)
		#print("COMMIT MESSAGE: ", commitmessage)
		#return
		for fileName, stats in commitFiles.items():
			print("RUNNING")
			if fileName not in self.files:
				cd = re.search(DateRegex, commitmessage)
				print("Cd: ", cd)
				if cd is not None:
					month = MonthToNum(cd.group(1))
					creation = date(int(cd.group(3)), month, int(cd.group(2)))
					start = reqStartDate
					age = (creation - start).total_seconds() / 604800
				else:
					age = 0 
				self.addNew(fileName, stats, len(commitFiles) - 1, age, commitmessage)
			else:
				self.updateFile(fileName, stats, len(commitFiles) - 1, commitmessage)
    
    #New entry for files added to the indexes related to the statistics of a class
	def addNew(self, fileName, stats, chgSetSize, age, message):
		entry = {
			'size' : 0,
			'LOC_touched' : stats['lines'],
			'NR' : 1,
			'Nfix' : 0,
			'NAuth' : [],
			'LOC_added' : stats['insertions'],
			'MAX_LOC_added' : stats['insertions'],
			'AVG_LOC_added' : stats['insertions'],
			'Churn' : stats['insertions'] - stats['deletions'],
			'MAX_Churn' : stats['insertions'] - stats['deletions'],
			'AVG_Churn' : stats['insertions'] - stats['deletions'],
			'ChgSetSize' : chgSetSize,
			'MAX_ChgSet' : chgSetSize,
			'AVG_ChgSet' : chgSetSize,
			'Age' : age,
			'WeightedAgeTotal' : 0,
			'WeightedAge' : 0,
			'NBugs' : 0
		}
		self.files.update({fileName : entry})  
    
	#Update a classes statistics in the array of files
	def updateFile(self, fileName, stats, chgSetSize, commitmessage):
		print("updating file")
		entry = self.files[fileName]
		entry['NR'] += 1
		entry['LOC_touched'] += stats['lines']
		self.update_loc_added(entry, stats)
		self.update_weighted_age(entry, stats)
		self.update_churn(entry, stats)
		self.update_chgSetSize(entry, stats, chgSetSize)
		self.update_num_fixes(entry, stats, commitmessage)
		self.update_num_authors(entry, stats, commitmessage)
		
	#Helper functions to compute the required updates to files in array of files 
	def update_weighted_age(self, entry, stats):
		if entry['Age'] != 0:
			entry['WeightedAgeTotal'] +=  entry['Age'] * int(entry['LOC_added'])
			entry['WeightedAge'] = entry['WeightedAgeTotal'] / entry['Age']
	

	def update_num_authors(self, entry, stats, message):
		match = re.search(AuthorRegex, message)
		if match :
			auth = str(match.group(1))
		if  auth not in list(entry['NAuth']):
			entry['NAuth'].append(auth)

	def update_loc_added(self, entry, stats):
		entry['LOC_added'] += stats['insertions']
		if (stats['insertions'] > entry['MAX_LOC_added']):
			entry['MAX_LOC_added'] = stats['insertions']
		entry['AVG_LOC_added'] = float(entry['LOC_added']) / entry['NR']
    
	def update_num_fixes(self, entry, stats, message):
		match = re.search(FixRegex, message)
		if match :
			entry['Nfix'] += 1

	def update_churn(self, entry, stats):
		entry['Churn'] += (stats['insertions'] - stats['deletions'])
		if (entry['Churn'] > entry['MAX_Churn']):
			entry['MAX_Churn'] = entry['Churn']
		entry['AVG_Churn'] = float(entry['Churn']) / entry['NR']
    
	def update_chgSetSize(self, entry, stats, chgSetSize):
		entry['ChgSetSize'] += chgSetSize
		if (chgSetSize > entry['MAX_ChgSet']):
			entry['MAX_ChgSet'] = chgSetSize
		entry['AVG_ChgSet'] = float(entry['ChgSetSize']) / entry['NR']

    	        
	def update_BeginningSize(self, commitobj, start):
		print("start: ", start)
		print("commits: ", len(commits))
		stat = commitobj.stats
		commitFiles = stat.files
		for fileName, stats in commitFiles.items():
			print("stats: ", stats)
			print("Filename: ", fileName)
			if fileName in self.files:
				print("got here")
				entry = self.files[fileName]
				fullString = str(os.getcwd()) + "/tika-app/" + fileName
				print("File name: ", str(fileName))
				print("commit: ", str(commitobj))
				try:
					#fullPath = subprocess.check_output("find . ")
					fullFile = subprocess.check_output("git show {}:\"{}\"".format(str(commitobj), str(fileName)), shell=True)
					f = tempfile.NamedTemporaryFile(delete=False)
					f.write(fullFile)
					f.close()
					numLines = 0
					with open(f.name) as f:
						for i, l in enumerate(f):
							pass
					numLines = i + 1;
					#numLines = subprocess.check_output("find . -name */{} | xargs wc -l".format(f.name), shell=True)
					print("NUMBER OF LINES: ", numLines)
					os.unlink(f.name)
					#endingCode = subprocess.check_output("wc -l "+ str(fullString), shell=True)
					#print("Lines of code for the file: ", endingCode)
					entry['size'] += numLines#(stats['insertions'] - stats['deletions'])
				except:
					print("could not read filename ", fileName)
#class for Classes
class Class:
	creationDate = ""
	authors = []
	bugfixes = []
	waschanged = ""
	def __init__(self, name):
		self.name = name

def getBugs():
	jira = JIRA('https://issues.apache.org/jira/')
	#Gets all the issues from a Jira instance that are requirements and resolved
	issues = jira.search_issues('project = ' + sys.argv[2] + ' AND issuetype = "Bug" AND status in (Resolved, Closed) ORDER BY resolved ASC', maxResults=10000000)
	#Gets all the issues from a Jira instance that are requirements and not complete
	#issuesopen = jira.search_issues('project = ' + sys.argv[2] + ' AND issuetype = "New Feature" AND status in (Open, "In Progress", Reopened) ORDER BY updated ASC, resolved ASC', maxResults=10000000)
	#List to store all project requirements
	projectRequirements = []
	for issue in issues:
		creationDate = (issue.fields.created.encode('utf-8').strip()).split('-')
		resolutionDate = (issue.fields.resolutiondate.encode('utf-8').strip()).split('-')
		#Set the name of the project here
		#Get the requirement name from the Jira issue
		requirement = Requirement(issue.key.encode('utf-8').strip())
		#Get the creation date of the requirement from the Jira issue
		creationDate = (issue.fields.created.encode('utf-8').strip()).split('-')
		#Get the resolution date of the requirement from the Jira issue
		resolutionDate = (issue.fields.resolutiondate.encode('utf-8').strip()).split('-')
		filewriter.writerow([sys.argv[2], requirement.name])
		##print "This is the requirment name" + requirement.name + ":\n\n"
		#print creationDate

		#Format the dates
		creationDate[2] = creationDate[2][:2]
		resolutionDate[2] = resolutionDate[2][:2]
		reqCreationDate = creationDate[0] + "-" + creationDate[1] + "-" + 			creationDate[2] 
		reqResolutionDate = resolutionDate[0] + "-" + resolutionDate[1] + "-" + resolutionDate[2]
		
		#print "git log --since=" + reqCreationDate + " --until=" + reqResolutionDate + " --grep=\'" + requirement.name + "\'"
		print ("Creation date: {}".format(reqCreationDate))
		print ("Resolution date: {}".format(reqResolutionDate))
		#Check out the master branch again to go backwards in the gitlog
		#Get all the commits since creation of the requirment to its resolution	
		output = subprocess.check_output("git log --since=" + reqCreationDate + " --until=" + reqResolutionDate + " --grep=\'" + requirement.name + "\'", shell=True)
		#Search the commits and find all the SHA-1 hashes of each commit and put them in a list
		commits = re.findall(commitHashRegex, output)
	
		print "Requirement name " + requirement.name
		print "Number of commits " + str(len(commits))
	
		'''done = False
		#Check for the number of commits to be atleast 1
		if (len(commits) > 0):
			print("should get here")
			commitmessages = output.split('\n\n')
			#Go through each commit in requirement
			f = Files()
			requirementcreation = date(int(creationDate[0]), int(creationDate[1]), int(creationDate[2]))
			f.updateCommits(commits, requirement.name, 0, requirementcreation)
			print("files length: ", len(f.files))
			items = f.files.items()
			print("Length of items:", len(items))
			for fileName, stats in items:
				print("HEY LOOK")
				#items = stats.iteritems()
				filewriter.writerow([("%s,%s,%s" % (sys.argv[2], "", fileName)),
				("%d" % (stats['size'])),
				("%d" % (stats['LOC_touched'])),
				("%d" % (stats['NR'])),
				("%d" % (stats['Nfix'])),
				("%d" % (len(stats['NAuth']))),
				("%d" % (stats['LOC_added'])),
				("%d" % (stats['MAX_LOC_added'])),
				("%.2f" % (stats['AVG_LOC_added'])),
				("%d" % (stats['Churn'])),
				("%d" % (stats['MAX_Churn'])),
				("%.2f" % (stats['AVG_Churn'])),
				("%d" % (stats['ChgSetSize'])),
				("%d" % (stats['MAX_ChgSet'])),
				("%.2f" % (stats['AVG_ChgSet'])),
				("%d" % (stats['Age'])),
				("%d" % (stats['WeightedAge']))])'''
				


#Requirement Class
class Requirement:
	#classes that were available in requirement
	classes = []
	#hashes of all commits involved in requirement
	commitHashes = []
	def __init__(self, name):
		self.name = name
	def addClass(self, classname, changed):
		classes.append(classname)
		waschanged.append(changed)





for x in range(0, len(sys.argv)):
	print("argument: ", sys.argv[x])
if (len(sys.argv) != 3):
	print "Error incorrect number of arguments"
else:
	#Changes directory to that of the project in which the git files are located
	#Must be adjusted depending on the environment being worked on
	#ADD FUNCTIONALITY TO SPECIFY DIRECTORY
	initialFolder = os.path.abspath(os.curdir)
	os.chdir(sys.argv[1])
	listOfTagDates = getAllTags(sys.argv[1])
	listOfTagDates.sort(key=lambda x: x[1])
	print("YOOOOOOOOOO")
	print(listOfTagDates)
	#sys.exit(0)
	os.path.abspath(os.curdir)
	output = subprocess.check_output("git log --since=2007-09-27 --until=2013-09-27", shell=True)

	#Specifies the path the repository for the project is in
	#Uses this repository to gather statistics
	repo = Repo(".")#sys.argv[1])
	assert not repo.bare
	#Regex to extract the SHA-1 hashes from commit messages
	commitHashRegex = r'\b([a-f0-9]{40})\b'
	#Regex to extract the Author of the commit from commit messages
	commitAuthorRegex = r'Author: ([ a-zA-Z]*)'
	#Sets Jira instance in order to gather requirements from
	jira = JIRA('https://issues.apache.org/jira/')
	#Gets all the issues from a Jira instance that are requirements and resolved
	issues = jira.search_issues('project = ' + sys.argv[2] + ' AND issuetype = "New Feature" AND status in (Resolved, Closed) ORDER BY resolved ASC', maxResults=10000000)
	#Gets all the issues from a Jira instance that are requirements and not complete
	issuesopen = jira.search_issues('project = ' + sys.argv[2] + ' AND issuetype = "New Feature" AND status in (Open, "In Progress", Reopened) ORDER BY updated ASC, resolved ASC', maxResults=10000000)
	#List to store all project requirements
	projectRequirements = []
	for issue in issues:
		#Get the requirement name from the Jira issue
		requirement = Requirement(issue.key.encode('utf-8').strip())
		#Get the creation date of the requirement from the Jira issue
		creationDate = (issue.fields.created.encode('utf-8').strip()).split('-')
		#Get the resolution date of the requirement from the Jira issue
		resolutionDate = (issue.fields.resolutiondate.encode('utf-8').strip()).split('-')
		#filewriter.writerow([sys.argv[2], requirement.name])
		##print "This is the requirment name" + requirement.name + ":\n\n"
		#print creationDate

		#Format the dates
		creationDate[2] = creationDate[2][:2]
		resolutionDate[2] = resolutionDate[2][:2]
		reqCreationDate = creationDate[0] + "-" + creationDate[1] + "-" + 			creationDate[2] 
		reqResolutionDate = resolutionDate[0] + "-" + resolutionDate[1] + "-" + resolutionDate[2]
		print("req resolution date: ", reqResolutionDate)
		for x in range(0, len(listOfTagDates)):
			reqDateFormat = datetime.strptime(reqResolutionDate, "%Y-%m-%d")
			tagDate = datetime.strptime(listOfTagDates[x][1], "%Y-%m-%d")
			if reqDateFormat > tagDate:
				continue
			else:
				if listOfTagDates[x] in tagTikaDict:
					tagTikaDict[listOfTagDates[x]].append(issue)
				else:
					tagTikaDict[listOfTagDates[x]] = [issue]
				break

	for key, value in sorted(tagTikaDict.items()):
		print("associated issues for ", key)
		for eachIssue in value:
			print(eachIssue)
	#sys.exit(0)

	#Set the name of the project here
	#ADD Command Line arguments to specify project name
	project = 'Tika'
	#open a csv to write Class changes for a project and its requirements
	with open(str(sys.argv[2]) + '.csv', 'wb+') as csvfile:
		#Write Row to CSV
		filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', 				quoting=csv.QUOTE_MINIMAL)
		filewriter.writerow(['Project ID', 'Requirement ID', 'Class Name',
					    "Size at beginning of release",
					    "LOC_touched",
					    "NR",
					    "Nfix", 
					    "NAuth",
					    "LOC_added", 
					    "MAX_LOC_added", 
					    "AVG_LOC_added", 
					    "Churn", 
					    "MAX_Churn", 
					    "AVG_Churn", 
					    "ChgSetSize", 
					    "MAX_ChgSet", 
					    "AVG_ChgSet", 
					    "Age", 
					    "WeightedAge"])
		subprocess.check_output("git checkout -f master", shell=True)
		for tagKey, issueList in sorted(tagTikaDict.items()):
			filewriter.writerow(tagKey)
			issues = issueList
			#Go through every requirement in Jira
			for issue in issues: 
				#Get the requirement name from the Jira issue
				requirement = Requirement(issue.key.encode('utf-8').strip())
				#Get the creation date of the requirement from the Jira issue
				creationDate = (issue.fields.created.encode('utf-8').strip()).split('-')
				#Get the resolution date of the requirement from the Jira issue
				resolutionDate = (issue.fields.resolutiondate.encode('utf-8').strip()).split('-')
				filewriter.writerow([sys.argv[2], requirement.name])
				##print "This is the requirment name" + requirement.name + ":\n\n"
				#print creationDate

				#Format the dates
				creationDate[2] = creationDate[2][:2]
				resolutionDate[2] = resolutionDate[2][:2]
				reqCreationDate = creationDate[0] + "-" + creationDate[1] + "-" + 			creationDate[2] 
				reqResolutionDate = resolutionDate[0] + "-" + resolutionDate[1] + "-" + resolutionDate[2]
				
				#print "git log --since=" + reqCreationDate + " --until=" + reqResolutionDate + " --grep=\'" + requirement.name + "\'"
				#print reqCreationDate
				#print reqResolutionDate
				#Check out the master branch again to go backwards in the gitlog
				#Get all the commits since creation of the requirment to its resolution	
				
				print("HEY LOOK", reqCreationDate)
				output = subprocess.check_output("git log --since=" + reqCreationDate + " --until=" + reqResolutionDate + " --grep=\'" + requirement.name + "\'", shell=True)
				#Search the commits and find all the SHA-1 hashes of each commit and put them in a list
				commits = re.findall(commitHashRegex, output)
			
				print "Requirement name " + requirement.name
				#print reqCreationDate
				#print reqResolutionDate
				print "Number of commits " + str(len(commits))
			
				done = False
				#Check for the number of commits to be atleast 1
				if (len(commits) > 0):
					print("should get here")
					commitmessages = output.split('\n\n')
					#Go through each commit in requirement
					f = Files()
					requirementcreation = date(int(creationDate[0]), int(creationDate[1]), int(creationDate[2]))
					f.updateCommits(commits, requirement.name, 0, requirementcreation)
					print("files length: ", len(f.files))
					items = f.files.items()
					print("Length of items:", len(items))
					for fileName, stats in items:
						print("HEY LOOK")
						#items = stats.iteritems()
						filewriter.writerow([("%s,%s,%s" % (sys.argv[2], "", fileName)),
						("%d" % (stats['size'])),
						("%d" % (stats['LOC_touched'])),
						("%d" % (stats['NR'])),
						("%d" % (stats['Nfix'])),
						("%d" % (len(stats['NAuth']))),
						("%d" % (stats['LOC_added'])),
						("%d" % (stats['MAX_LOC_added'])),
						("%.2f" % (stats['AVG_LOC_added'])),
						("%d" % (stats['Churn'])),
						("%d" % (stats['MAX_Churn'])),
						("%.2f" % (stats['AVG_Churn'])),
						("%d" % (stats['ChgSetSize'])),
						("%d" % (stats['MAX_ChgSet'])),
						("%.2f" % (stats['AVG_ChgSet'])),
						("%d" % (stats['Age'])),
						("%d" % (stats['WeightedAge']))])
					


	##with open(sys.argv[2] + '.csv','wb') as file:
						##("Project ID," \
						    	##"Class ID," \
						    #"Requirement ID," \
						    #"Size at beginning of release," \
						    #"LOC_touched," \
						    #"NR," \
						    #"Nfix," \
						    #"NAuth," \
						    #"LOC_added," \
						    #"MAX_LOC_added," \
						    #"AVG_LOC_added," \
						    #"Churn," \
						    #"MAX_Churn," \
						    #"AVG_Churn," \
						    #"ChgSetSize," \
						    #"MAX_ChgSet," \
						    #"AVG_ChgSet," \
						    #"Age," \
						    #"WeightedAge" \
						    #"\n"
						    ##)'
						'''
						THIS CODE IS UNUSED BUT MAY CONTAIN HELPFUL WAYS TO IMPLEMENT FUTURE UPDATES
						i = 0
						commitobj = repo.commit(commit)
						stat = commitobj.stats
						commitfiles = stat.files
						print commitobj.message + "\n\n"
						#Add to the list of hashes for a commit in a requirement
						requirement.commitHashes.append(commit)
						#Get all the classes in changed in a commit
						classes = subprocess.check_output("git diff-tree --no-commit-id --name-only -r " + commit + " | grep \'\.java\' || true" , shell=True)
						classes = classes.split('\n')'''
					'''#Go thru the classes
					for name in commitfiles:
							#Check if the class is already in requirement class list
							#Meaning check if class was already in the project at start of requiremnt or not
							for classname in requirement.classes:
								if (name != '\n' and  classname.name == name):
									print classname.name  
									print name 
								#Check to make sure class isn't just a newline character
								#Extract author's name from commit
								#If class in list then changed its state
									author = re.search(commitAuthorRegex, commitmessages[i])
									requirement.classes[classes.index(name)].waschanged = "YES"
									if author is not None and  author not in requirement.classes[classes.index(name)].authors:
										requirement.classes[classes.index(name)].authors.append(author.group(1))
										print requirement.classes[classes.index(name)].authors
									done = True
									break'''

