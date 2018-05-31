#AUTHORS
#TYELER BRIDGES
#TINA RICKARD
#MAX MOEDE
from jira import JIRA
from git import Repo
import tempfile
import json
import time
from time import strptime
import csv
import subprocess
import os
import re
import git
import sys
import itertools
from datetime import date, timedelta, datetime
#Regular expressions to extract date, author, and whether requirement was bug fix or not
DateRegex = r'Date:   [A-Za-z]{3} ([A-Za-z]{3}) ([0-9]{1,2}) [A-Za-z0-9:]{8} ([0-9]{4})'	
FixRegex = r' (fix) '
AuthorRegex = r'Author: ([A-Za-z ]+)'
initialFolder = ""
bugRegex = r'bug[# \t]*[0-9]+'
prRegex = r'pr[# \t]*[0-9]+'
showBugRegex = r'show\_bug\.cgi\?id=[0-9]+'
bug2Regex = r'\[[0-9]+\]'
bashDiffFunc = "bashScript"
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



def getBugs():
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
		comHashHist = r'commit ([a-zA-Z0-9]*)'
		#Sets Jira instance in order to gather requirements from
		jira = JIRA('https://issues.apache.org/jira/')

		block_size = 150
		block_num = 0
		totalIssues = []
		while True:
			start_idx = block_num*block_size
			issues = jira.search_issues('project = ' + sys.argv[2] + ' AND issuetype = "Bug" AND status in (Resolved, Closed) ORDER BY resolved ASC', start_idx, block_size)
			for issue in issues:
				totalIssues.append(issue)
			#totalIssues.append(issues)
			if len(issues) == 0:
			# Retrieve issues until there are no more to come
				break
			block_num += 1
	        #for issue in issues:
	        #    log.info('%s: %s' % (issue.key, issue.fields.summary))

		#Gets all the issues from a Jira instance that are requirements and resolved
		#issues = jira.search_issues('project = ' + sys.argv[2] + ' AND issuetype = "Bug" AND status in (Resolved, Closed) ORDER BY resolved ASC', maxResults=10000000)
		#Gets all the issues from a Jira instance that are requirements and not complete
		#issuesopen = jira.search_issues('project = ' + sys.argv[2] + ' AND issuetype = "New Feature" AND status in (Open, "In Progress", Reopened) ORDER BY updated ASC, resolved ASC', maxResults=10000000)
		#List to store all project requirements
		projectRequirements = []
		count = 0
		print("Total Issues: {}".format(len(totalIssues)))
		bugDict = {}
		for issue in totalIssues:
			try:
				subprocess.check_output("git checkout -f master", shell=True)
				creationDate = (issue.fields.created.encode('utf-8').strip()).split('-')
				resolutionDate = (issue.fields.resolutiondate.encode('utf-8').strip()).split('-')
				#Set the name of the project here
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
				
				#print "git log --since=" + reqCreationDate + " --until=" + reqResolutionDate + " --grep=\'" + requirement.name + "\'"
				#print ("Creation date: {}".format(reqCreationDate))
				#print ("Resolution date: {}".format(reqResolutionDate))
				#Check out the master branch again to go backwards in the gitlog
				#Get all the commits since creation of the requirment to its resolution	
				output = subprocess.check_output("git log --since=" + reqCreationDate + " --until=" + reqResolutionDate + " --grep=\'" + requirement.name + "\'", shell=True)
				#Search the commits and find all the SHA-1 hashes of each commit and put them in a list
				commits = re.findall(commitHashRegex, output)
				#print("New bug.....")
				#print ("Creation date: {}".format(reqCreationDate))
				#print ("Resolution date: {}".format(reqResolutionDate))
				if len(commits) != 0:
					mostRecentCommit = commits[0]
					#print("related commit: {}".format(mostRecentCommit))
					comComment = subprocess.check_output("git log --format=%B -n 1 {}".format(mostRecentCommit), shell=True)
					#print("comment: {}".format(comComment))
					previousCommit = subprocess.check_output("git log -1 --before {}".format(reqResolutionDate), shell=True)
					pcHash = re.findall(commitHashRegex, previousCommit)[0]
					#print("previous commit: ", pcHash)
					
					#print("next commit: {}".format(previousCommit))
					difference = subprocess.check_output("git diff -U0 {} {} | ../../SURPCODE/bashScript.sh".format(pcHash, mostRecentCommit), shell=True) #--stat instead of name only
					#print("difference: \n{}".format(difference))
					lineGroups = []
					commitFiles = difference.split("\n")
					commitFiles = [x for x in commitFiles if not (x.isspace() or not x)]
					currentLine = -1
					continuedLine = -1
					givenStartLine = -1
					continuing = False
					for eachC in commitFiles:
						#print("each line from commit: {}".format(eachC))
						try:
							splitLine = eachC.split(":")
							#print("Split line: {}".format(splitLine))
							lineNum = splitLine[1]
							#print("line Num: ", lineNum)
							if int(lineNum) == currentLine:
								if continuing == False:
									lineGroups.append((splitLine[0], continuedLine, continuedLine))
									givenStartLine = int(lineNum)
									continuing = True
								continuedLine += 1
							else:
								if continuing == True:
									lineGroups.append((splitLine[0], givenStartLine, continuedLine))
									continuing = False
									givenStartLine = int(lineNum)
								continuedLine = int(lineNum)
								currentLine = int(lineNum)
							#print("actual Line number: {}".format(continuedLine))
						except:
							print("could not find the line number")
					#print("LINE GROUPS AFFECTED: {}".format(lineGroups))
					#print ("Creation date: {}".format(reqCreationDate))
					splitDate = reqCreationDate.split("-")
					bugInitDate = datetime(int(splitDate[0]), int(splitDate[1]), int(splitDate[2]), 0, 0)
					#print("BUG INIT DATE: {}".format(bugInitDate))
					closestToInitDate = None
					closestComHash = None
					subprocess.check_output("git checkout {}".format(mostRecentCommit), shell=True)
					for eachGroup in lineGroups:
						#print("new lines looking at...")
						if ".java" in eachGroup[0]:
							try:
								historyOfLine = subprocess.check_output("git log -u -L {},{}:{}".format(eachGroup[1], eachGroup[2], eachGroup[0]), shell=True)
								#print("History: {}".format(historyOfLine))
								comD = re.findall(comHashHist, historyOfLine)
								cd = re.findall(DateRegex, historyOfLine)
								#print("Cd: ", cd)
								#print("Commit hash: ", comD)
								for x in range(0, len(cd)):
									#print("edit date: ", cd[x])
									editTime = datetime(int(cd[x][2]), strptime(cd[x][0], '%b').tm_mon, int(cd[x][1]), 0, 0)
									if editTime < bugInitDate:
										if closestToInitDate is None:
											closestToInitDate = editTime
											closestComHash = comD[x]
										elif editTime > closestToInitDate:
											closestToInitDate = editTime
											closestComHash = comD[x]
									#print("EDIT TIME: {}".format(editTime))
							except:
								print("could not find lines")
							#if cd is not None:
						#		month = MonthToNum(cd.group(1))
						#		creation = date(int(cd.group(3)), month, int(cd.group(2)))
					
					if closestComHash in bugDict:
						bugDict[closestComHash] += 1
					else:
						bugDict[closestComHash] = 1
					print("bug init date: ", bugInitDate)
					print("bug commit date: ", closestToInitDate)
					print("BUG DICTIONARY: ", bugDict)
			except:
				print("something with this issue broke...")	
		with open('issueRoots.csv', 'wb') as csv_file:
			writer = csv.writer(csv_file)
			for key, value in bugDict.items():
				writer.writerow([key, value])
				
				#filesChanged = difference.split("\n")
				#for fChanged in filesChanged:
					#eachWord = fChanged.split(" ")
					#if len(eachWord) > 1:
					#	fileLocation = eachWord[1]
					#	if "." in fileLocation:
					#		print("file location: {}".format(fileLocation))
							#commitFiles.append(fileLocation)
		'''subprocess.check_output("git checkout {}".format(mostRecentCommit), shell=True)
				for fChanged in commitFiles:
					blameHistory = ""
					print("file string: |||{}|||".format(fChanged))
					try:
						blameHistory = subprocess.check_output("git blame {}".format(fChanged), shell=True)
					except:
						subprocess.check_output("git checkout {}".format(pcHash), shell=True)
						try:
							blameHistory = subprocess.check_output("git blame {}".format(fChanged), shell=True)
						except:
							print("can't find blame history for file.")
						subprocess.check_output("git checkout {}".format(mostRecentCommit), shell=True)
					splitBlame = blameHistory.split("\n")
					fileHashes = []
					lineNum = 0
					for eachLine in splitBlame:
						#print("each Line: |||{}|||".format(eachLine))
						lineNum += 1
						eachWord = eachLine.split(" ")
						comHash = eachWord[0]
						print("each Hash: {} for line {}".format(comHash, lineNum))
						fileHashes.append((comHash, lineNum))'''


					#print("Blame history: {}".format(blameHistory))


				#return
				#count += 1
				#print("should get here")
				#commitmessages = output.split('\n\n')
				#Go through each commit in requirement
				#f = Files()
				#requirementcreation = date(int(creationDate[0]), int(creationDate[1]), int(creationDate[2]))
				#f.updateCommits(commits, requirement.name, 0, requirementcreation)
				#print("files length: ", len(f.files))
				#items = f.files.items()
				#print("Length of items:", len(items))

			#print "Requirement name " + requirement.name
			#print "Number of commits " + str(len(commits))
		#print("Total issues: {}".format(count))


def main():
	getBugs()


if __name__ == '__main__':
	main()
