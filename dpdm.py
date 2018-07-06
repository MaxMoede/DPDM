#MAX MOEDE
from jira import JIRA
from git import Repo
import tempfile
import json
import time
import csv
import subprocess
from subprocess import PIPE
import os, errno
import re
import git
import sys
import itertools
import shutil
from datetime import date, timedelta, datetime
from getTags import *
from getSmells import *


alreadyUsedIssues = {}

def getRepo(projectPath):
	initialFolder = os.path.abspath(os.curdir)
	repoPath = initialFolder + "/" + projectPath
	repo = Repo(repoPath)
	return repo

def getReleases(projectPath, repo):
	finalTags = []
	tagTuples = []
	os.chdir(projectPath)
	bunchOfTags = subprocess.check_output("git tag", shell=True)
	listOfTags = bunchOfTags.split("\n")

	for tag in listOfTags:
		if tag not in finalTags and tag is not '':
			finalTags.append(tag)

	for tag in finalTags:
		fullDate = subprocess.check_output("git log -1 --format=%ai {}".format(tag), shell=True)
		newDate = fullDate.split(" ")[0]
		commitHashWithNewline = subprocess.check_output("git rev-parse {}^{{}}".format(tag), shell=True)
		commitHash = commitHashWithNewline.rstrip('\n')
		commitObj = repo.commit(commitHash)
		tagTuples.append((tag, commitObj, newDate))
	tagTuples.sort(key=lambda x: datetime.strptime(x[2], '%Y-%m-%d'))
	return tagTuples

def sizeAtBeginningOfRelease(tagTuple):
	print("getting size at beginning of release...")
	commitObj = tagTuple[1]
	tagName = tagTuple[0]
	unaccountedFileNames = []
	foundFileNames = []
	fileSizes = []

	firstCmd = "git ls-files"
	firstPs = subprocess.Popen(firstCmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
	listOfFileNames = firstPs.communicate()[0].split('\n')
	for eachFileName in listOfFileNames:
		if ".java" in eachFileName:
			unaccountedFileNames.append(eachFileName)
	#Have to get last commit of previous release,
	#Which is the previous commit of the corresponding tag
	previousCommit = subprocess.check_output("git show {}^1".format(commitObj.hexsha), shell=True)
	previousComHash = previousCommit.split()[1]
	subprocess.check_output("git checkout -f {}".format(previousComHash), shell=True)
	#gets a tree of all files with corresponding line numbers
	cmd = "git ls-files | xargs wc -l"
	ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
	newOutput = ps.communicate()[0].split('\n')

	for file in newOutput:
		#filter for java files
		if ".java" in file:
			fileTuple = file.split()
			if len(fileTuple) > 1:
				linesOfCode = fileTuple[0]
				fileName = fileTuple[1]
				print("file name: {}".format(fileName))
				foundFileNames.append(fileName)
				fileSizes.append((tagName, fileName, linesOfCode))
	for eachUnaccountedName in unaccountedFileNames:
		if eachUnaccountedName in foundFileNames:
			print("good")
		else:
			#if "ExcelExtractor" in eachUnaccountedName:
			#	print("found it")
			#	sys.exit(0)
			fileSizes.append((tagName, eachUnaccountedName, 0))
		#elif eachUnaccountedName not in foundFileNames:
			#print("found unaccounted name: {}".format(eachUnaccountedName))
	#sys.exit(0)
	return fileSizes

def num_revisions(tagTuple, fileSizes, tagTuples, repo):
	print("getting number of revisions per file...")
	timesTouchedDict = {}
	commitObj = tagTuple[1]
	linesTouchedDict = {}
	version_index = tagTuples.index(tagTuple)
	nextVersionTuple = tagTuples[version_index + 1]
	nextVersionHash = nextVersionTuple[1]
	justFiles = getFilesFromSizes(fileSizes)
	for file in justFiles:
		timesTouchedDict[file] = 0
	listOfComHashes = get_list_of_coms_between_versions(commitObj.hexsha, nextVersionHash.hexsha)
	for shortHash in listOfComHashes:
		comObj = repo.commit(shortHash)
		filesTouched = subprocess.check_output("git diff-tree --no-commit-id --name-only -r {}".format(comObj.hexsha), shell=True).split('\n')
		for fileTouched in filesTouched:
			if fileTouched in timesTouchedDict:
				timesTouchedDict[fileTouched] += 1
			else:
				timesTouchedDict[fileTouched] = 1
	return timesTouchedDict

def num_authors(tagTuple, fileSizes, tagTuples, repo):
	print("getting number of authors per file...")
	totAuthDict = {}
	authDict = {}
	authList = []
	commitObj = tagTuple[1]
	linesTouchedDict = {}
	version_index = tagTuples.index(tagTuple)
	nextVersionTuple = tagTuples[version_index + 1]
	nextVersionHash = nextVersionTuple[1]
	justFiles = getFilesFromSizes(fileSizes)

	for file in justFiles:
		authDict[file] = []
	listOfComHashes = get_list_of_coms_between_versions(commitObj.hexsha, nextVersionHash.hexsha)

	for shortHash in listOfComHashes:
		comObj = repo.commit(shortHash)
		#subprocess gives files touched for a commit
		filesTouched = subprocess.check_output("git diff-tree --no-commit-id --name-only -r {}".format(comObj.hexsha), shell=True).split('\n')
		for fileTouched in filesTouched:
			if fileTouched in authDict:
				if comObj.author.name not in authDict[fileTouched]:
					authDict[fileTouched].append(comObj.author.name)
			else:
				authDict[fileTouched] = [comObj.author.name]
	for fileName, authList in authDict.items():
		totAuthDict[fileName] = len(authList)
	return totAuthDict


def churn(linesTouchedDict):
	print("calculating churn...")
	churnDict = {}
	for key, linesTouchedTuple in linesTouchedDict.items():
		churnDict[key] = linesTouchedTuple[0] - linesTouchedTuple[1]
	return churnDict


def chg_set_size(tagTuple, fileSizes, tagTuples, repo):
	print("calculating chg set...")
	commitObj = tagTuple[1]
	chgSetsNumDict = {}
	chgSetsDict = {}
	version_index = tagTuples.index(tagTuple)
	nextVersionTuple = tagTuples[version_index + 1]
	nextVersionHash = nextVersionTuple[1]
	justFiles = getFilesFromSizes(fileSizes)

	for file in justFiles:
		chgSetsDict[file] = []
	listOfComHashes = get_list_of_coms_between_versions(commitObj.hexsha, nextVersionHash.hexsha)

	for x in range(0, len(listOfComHashes)-1):
		firstCom = listOfComHashes[x]
		secondCom = listOfComHashes[x+1]
		firstCom = repo.commit(firstCom).hexsha
		secondCom = repo.commit(secondCom).hexsha
		numStatOutput = subprocess.check_output("git diff --numstat {}..{}".format(firstCom, secondCom), shell=True)
		eachFileChanges = numStatOutput.split('\n')
		filesInCommit = []
		for eachFileInfo in eachFileChanges:
			changedElements = eachFileInfo.split()
			if len(changedElements) == 3:
				fileName = changedElements[2]
				filesInCommit.append(fileName)
		for eachFileName in filesInCommit:
			if ".java" in eachFileName:
				if eachFileName not in chgSetsDict:
					chgSetsDict[eachFileName] = []
				for otherFile in filesInCommit:
					if otherFile != eachFileName and otherFile not in chgSetsDict[eachFileName]:
						chgSetsDict[eachFileName].append(otherFile)

	for key, filesList in chgSetsDict.items():
		chgSetsNumDict[key] = len(filesList)
	return chgSetsNumDict

def max_chg_set(tagTuple, fileSizes, tagTuples, repo):
	print("calculating max chg set...")
	commitObj = tagTuple[1]
	chgSetsNumDict = {}
	maxChgDict = {}
	version_index = tagTuples.index(tagTuple)
	nextVersionTuple = tagTuples[version_index + 1]
	nextVersionHash = nextVersionTuple[1]
	justFiles = getFilesFromSizes(fileSizes)
	for file in justFiles:
		maxChgDict[file] = 0
	listOfComHashes = get_list_of_coms_between_versions(commitObj.hexsha, nextVersionHash.hexsha)
	for x in range(0, len(listOfComHashes)-1):
		firstCom = listOfComHashes[x]
		secondCom = listOfComHashes[x+1]
		firstCom = repo.commit(firstCom).hexsha
		secondCom = repo.commit(secondCom).hexsha
		numStatOutput = subprocess.check_output("git diff --numstat {}..{}".format(firstCom, secondCom), shell=True)
		eachFileChanges = numStatOutput.split('\n')
		filesInCommit = []
		for eachFileInfo in eachFileChanges:
			changedElements = eachFileInfo.split()
			if len(changedElements) == 3:
				fileName = changedElements[2]
				filesInCommit.append(fileName)
		for eachFileName in filesInCommit:
			if ".java" in eachFileName:
				if eachFileName not in maxChgDict:
					maxChgDict[eachFileName] = 0
				totalRelatedFiles = len(filesInCommit) - 1
				oldRelatedFiles = maxChgDict[eachFileName]
				if totalRelatedFiles > oldRelatedFiles:
					maxChgDict[eachFileName] = totalRelatedFiles
	return maxChgDict

def avg_chg_set(tagTuple, fileSizes, tagTuples, repo):
	print("calculating avg chg set...")
	commitObj = tagTuple[1]
	avgChgDict = {}
	chgListDict = {}
	version_index = tagTuples.index(tagTuple)
	nextVersionTuple = tagTuples[version_index + 1]
	nextVersionHash = nextVersionTuple[1]
	#print("Next version tuple: ", nextVersionTuple)
	justFiles = getFilesFromSizes(fileSizes)
	for file in justFiles:
		chgListDict[file] = []
	#print("first commit: ", commitObj.hexsha)
	#print("next commit: ", nextVersionHash.hexsha)
	listOfComHashes = get_list_of_coms_between_versions(commitObj.hexsha, nextVersionHash.hexsha)
	for x in range(0, len(listOfComHashes)-1):
		firstCom = listOfComHashes[x]
		secondCom = listOfComHashes[x+1]
		firstCom = repo.commit(firstCom).hexsha
		secondCom = repo.commit(secondCom).hexsha
		numStatOutput = subprocess.check_output("git diff --numstat {}..{}".format(firstCom, secondCom), shell=True)
		eachFileChanges = numStatOutput.split('\n')
		filesInCommit = []
		for eachFileInfo in eachFileChanges:
			changedElements = eachFileInfo.split()
			if len(changedElements) == 3:
				fileName = changedElements[2]
				filesInCommit.append(fileName)
		for eachFileName in filesInCommit:
			if ".java" in eachFileName:
				if eachFileName not in chgListDict:
					chgListDict[eachFileName] = []
				totalRelatedFiles = len(filesInCommit) - 1
				chgListDict[eachFileName].append(totalRelatedFiles)
	for key, associatedFilesList in chgListDict.items():
		if not associatedFilesList:
			avgChgDict[key] = 0
		else:
			avgChgDict[key] = sum(associatedFilesList) / float(len(associatedFilesList))
		#print("avg change for {}: {}".format(key, avgChgDict[key]))
	return avgChgDict


def loc_touched(tagTuple, fileSizes, tagTuples, repo):
	print("calculating loc touched...")
	commitObj = tagTuple[1]
	linesTouchedDict = {}
	version_index = tagTuples.index(tagTuple)
	#try:
	nextVersionTuple = tagTuples[version_index + 1]
	nextVersionHash = nextVersionTuple[1]
	#print("Next version tuple: ", nextVersionTuple)
	justFiles = getFilesFromSizes(fileSizes)
	for file in justFiles:
		linesTouchedDict[file] = (0,0)
	#print("first commit: ", commitObj.hexsha)
	#print("next commit: ", nextVersionHash.hexsha)
	listOfComHashes = get_list_of_coms_between_versions(commitObj.hexsha, nextVersionHash.hexsha)
	for x in range(0, len(listOfComHashes)-1):
		firstCom = listOfComHashes[x]
		secondCom = listOfComHashes[x+1]
		firstCom = repo.commit(firstCom).hexsha
		secondCom = repo.commit(secondCom).hexsha
		#print("first com: {}, secondCom: {}".format(firstCom, secondCom))
		numStatOutput = subprocess.check_output("git diff --numstat {}..{}".format(firstCom, secondCom), shell=True)
		eachFileChanges = numStatOutput.split('\n')
		for eachFileChanged in eachFileChanges:
			changedElements = eachFileChanged.split()
			if len(changedElements) == 3 and ".java" in changedElements[2]:
				fileName = changedElements[2]
				if changedElements[2] not in linesTouchedDict:
					linesTouchedDict[fileName] = (int(changedElements[0]), int(changedElements[1]))
				else:
					#print(changedElements[0])
					oldTuple = linesTouchedDict[fileName]
					newLinesAdded = oldTuple[0] + int(changedElements[0])
					newLinesDeleted = oldTuple[1] + int(changedElements[1])
					newTuple = (newLinesAdded, newLinesDeleted)
					linesTouchedDict[fileName] = newTuple
	#for key, linesTouchedTuple in linesTouchedDict.items():
	#	print("fileName: {}".format(key))
	#	print("total lines added: {}".format(linesTouchedTuple[0]))
	#	print("total lines deleted: {}".format(linesTouchedTuple[1]))
	return linesTouchedDict

def total_loc_touched(linesTouchedDict):
	print("calculating total loc...")
	totDict = {}
	for key, addDelTuple in linesTouchedDict.items():
		totLinesTouched = addDelTuple[0] + addDelTuple[1]
		totDict[key] = totLinesTouched
	return totDict


def loc_avg(tagTuple, fileSizes, tagTuples, repo):
	print("calculating avg loc...")
	avgLinesDict = {}
	avgAddedLines = {}
	commitObj = tagTuple[1]
	linesTouchedDict = {}
	version_index = tagTuples.index(tagTuple)
	#try:
	nextVersionTuple = tagTuples[version_index + 1]
	nextVersionHash = nextVersionTuple[1]
	justFiles = getFilesFromSizes(fileSizes)
	for file in justFiles:
		linesTouchedDict[file] = ([], [])
		avgAddedLines[file] = 0
	listOfComHashes = get_list_of_coms_between_versions(commitObj.hexsha, nextVersionHash.hexsha)
	for x in range(0, len(listOfComHashes)-1):
		firstCom = listOfComHashes[x]
		secondCom = listOfComHashes[x+1]
		firstCom = repo.commit(firstCom).hexsha
		secondCom = repo.commit(secondCom).hexsha
		numStatOutput = subprocess.check_output("git diff --numstat {}..{}".format(firstCom, secondCom), shell=True)
		eachFileChanges = numStatOutput.split('\n')
		for eachFileChanged in eachFileChanges:
			changedElements = eachFileChanged.split()
			if len(changedElements) == 3 and ".java" in changedElements[2]:
				fileName = changedElements[2]
				if changedElements[2] not in linesTouchedDict:
					linesTouchedDict[fileName] = ([int(changedElements[0])], [int(changedElements[1])])
				else:
					oldTuple = linesTouchedDict[fileName]
					oldAddedList = oldTuple[0]
					oldAddedList.append(int(changedElements[0]))
					oldDeletedList = oldTuple[1]
					oldDeletedList.append(int(changedElements[1]))
					newTuple = (oldAddedList, oldDeletedList)
					linesTouchedDict[fileName] = newTuple
	for key, linesTouchedTuple in linesTouchedDict.items():
		aLinesList = linesTouchedTuple[0]
		dLinesList = linesTouchedTuple[1]
		if not aLinesList:
			avgLinesDict[key] = (0, 0)
		else:
			#print("fileName: {}".format(key))
			#print("added lines times: {}".format(aLinesList))
			#print("deleted lines times: {}".format(dLinesList))
			avgAdded = sum(aLinesList) / float(len(aLinesList))
			avgDeleted = sum(dLinesList) / float(len(dLinesList))
			#print("added avg: {}".format(avgAdded))
			#print("deleted avg: {}".format(avgDeleted))
			avgLinesDict[key] = (avgAdded, avgDeleted)
	for avgFileName, avgTuple in avgLinesDict.items():
		avgAddedLines[avgFileName] = avgTuple[0]
	return avgAddedLines


def churn_avg(tagTuple, fileSizes, tagTuples, repo):
	print("calculating avg churn...")
	avgChurnDict = {}
	commitObj = tagTuple[1]
	linesTouchedDict = {}
	version_index = tagTuples.index(tagTuple)
	#try:
	nextVersionTuple = tagTuples[version_index + 1]
	nextVersionHash = nextVersionTuple[1]
	justFiles = getFilesFromSizes(fileSizes)
	for file in justFiles:
		linesTouchedDict[file] = []
	listOfComHashes = get_list_of_coms_between_versions(commitObj.hexsha, nextVersionHash.hexsha)
	for x in range(0, len(listOfComHashes)-1):
		firstCom = listOfComHashes[x]
		secondCom = listOfComHashes[x+1]
		firstCom = repo.commit(firstCom).hexsha
		secondCom = repo.commit(secondCom).hexsha
		numStatOutput = subprocess.check_output("git diff --numstat {}..{}".format(firstCom, secondCom), shell=True)
		eachFileChanges = numStatOutput.split('\n')
		for eachFileChanged in eachFileChanges:
			changedElements = eachFileChanged.split()
			if len(changedElements) == 3 and ".java" in changedElements[2]:
				fileName = changedElements[2]
				#if "MidiParser.java" in fileName:
				#	print("Lines added/deleted for {}: {}/{}".format("midi parser", changedElements[0], changedElements[1]))
				if changedElements[2] not in linesTouchedDict:
					linesTouchedDict[fileName] = [int(changedElements[0]) - int(changedElements[1])]
				else:
					linesTouchedDict[fileName].append(int(changedElements[0]) - int(changedElements[1]))
	for key, linesTouchedList in linesTouchedDict.items():
		#print("key: {}... lines Touched list: {}".format(key, linesTouchedList))
		if not linesTouchedList:
			avgChurnDict[key] = 0
		else:
			avgChurn = sum(linesTouchedList) / float(len(linesTouchedList))
			avgChurnDict[key] = avgChurn
	return avgChurnDict



def loc_max(tagTuple, fileSizes, tagTuples, repo):
	print("calculating max loc....")
	commitObj = tagTuple[1]
	linesAddedDict = {}
	version_index = tagTuples.index(tagTuple)
	nextVersionTuple = tagTuples[version_index + 1]
	nextVersionHash = nextVersionTuple[1]
	justFiles = getFilesFromSizes(fileSizes)
	for file in justFiles:
		linesAddedDict[file] = 0
	listOfComHashes = get_list_of_coms_between_versions(commitObj.hexsha, nextVersionHash.hexsha)
	for x in range(0, len(listOfComHashes)-1):
		firstCom = listOfComHashes[x]
		secondCom = listOfComHashes[x+1]
		firstCom = repo.commit(firstCom).hexsha
		secondCom = repo.commit(secondCom).hexsha
		numStatOutput = subprocess.check_output("git diff --numstat {}..{}".format(firstCom, secondCom), shell=True)
		eachFileChanges = numStatOutput.split('\n')
		for eachFileChanged in eachFileChanges:
			changedElements = eachFileChanged.split()
			if len(changedElements) == 3 and ".java" in changedElements[2]:
				fileName = changedElements[2]
				if changedElements[2] not in linesAddedDict:
					linesAddedDict[fileName] = int(changedElements[0])
				else:
					oldLinesAdded = linesAddedDict[fileName]
					newLinesAdded = int(changedElements[0])
					if newLinesAdded > oldLinesAdded:
						linesAddedDict[fileName] = newLinesAdded
	return linesAddedDict

'''def runSonar(tagTuple):
	commitObj = tagTuple[1].hexsha
	#previousCommit = subprocess.check_output("git show {}^1".format(commitObj), shell=True)
	#previousComHash = previousCommit.split()[1]
	#print("previous commit hash: {}".format(previousComHash))
	try:
		subprocess.check_output("git checkout {}".format(commitObj), shell=True)
		subprocess.check_output("mvn clean install", shell=True)
		subprocess.check_output("mvn sonar:sonar ", shell=True)
	except subprocess.CalledProcessError as someError:
		print(someError)'''


def get_smells(tagTuple, fileSizes, tagTuples, repo, ruleIDs):
	print("calculating smells....")
	issueDict = {}
	ruleIDIssueDict = {}
	commitObj = tagTuple[1]
	commitHash = commitObj.hexsha
	justFiles = getFilesFromSizes(fileSizes)
	for file in justFiles:
		issueDict[file] = 0
	for file in justFiles:
		for eachRuleID in ruleIDs:
			fileAndRuleID = file + "\t" + str(eachRuleID)
			ruleIDIssueDict[fileAndRuleID] = 0
	previousCommit = subprocess.check_output("git show {}^1".format(commitHash), shell=True)
	previousComHash = previousCommit.split()[1]
	subprocess.check_output("git checkout {}".format(previousComHash), shell=True)
	try:
		p = subprocess.Popen(["mvn", "clean", "install", "-DskipTests=true", "-Dmaven.test.failure.ignore=true", "sonar:sonar", "-Dsonar.host.url=http://localhost:9000"], stdout=PIPE, stderr=PIPE)
		output, error = p.communicate()
		#print("output: {}".format(str(output)))
		if p.returncode != 0: 
			print("sonarqube failed %d %s %s" % (p.returncode, output, error))
			#sys.exit(0)
		else:
			issues = get_issues()
			if len(issues) < 0:
				print("getting smells failed.")
			#print("Issues: {}".format(issues))
			for eachIssue in issues:
				if eachIssue is not None:
					if eachIssue[2].decode("utf-8") not in alreadyUsedIssues:
						#print("RULE ID For issue: {}".format(eachIssue[1]))
						fileName = eachIssue[0].decode("utf-8")
						#print("fileName with an issue: {}".format(fileName))
						foundAMatch = 0
						correspondingRuleID = str(eachIssue[1])
						for eachFileName, numIssues in issueDict.items():
							fileAndRuleID = eachFileName + "\t" + correspondingRuleID
							if fileName in eachFileName and foundAMatch == 0:
								print("got a match in get smells. {} for {}".format(fileName, eachFileName))
								issueDict[eachFileName] += 1
								if fileAndRuleID in ruleIDIssueDict:
									ruleIDIssueDict[fileAndRuleID] += 1
								else:
									ruleIDIssueDict[fileAndRuleID] = 1
								foundAMatch = 1
							#if foundAMatch == 0:
							#	issueDict[fileName] = 1
							#	ruleIDIssueDict[fileAndRuleID] = 1
						if foundAMatch == 0:
							missingFileAndRuleID = fileName + "\t" + correspondingRuleID
							issueDict[fileName] = 1
							ruleIDIssueDict[missingFileAndRuleID] = 1

						alreadyUsedIssues[eachIssue[2].decode("utf-8")] = "Used"
			stringRuleIDs = [str(i) for i in ruleIDs]
			for eachFileName in issueDict.keys():
				SpecificFileRuleIDList = [x for x in ruleIDIssueDict.keys() if eachFileName in x]
				combinedSpecificList = '\t'.join(SpecificFileRuleIDList)
				#print("File list: {}".format(SpecificFileRuleIDList))
				missingRuleIDs = [j for j in stringRuleIDs if j not in combinedSpecificList]
				#print("Missing Rule IDs: {}".format(missingRuleIDs))
				for eachMissingRuleID in missingRuleIDs:
					newCombinedFileAndIssue = eachFileName + "\t" + eachMissingRuleID
					#print(newCombinedFileAndIssue)
					ruleIDIssueDict[newCombinedFileAndIssue] = 0
				
			#for eachRuleID in ruleIDs:
			#	for eachFileName, numProblems in issueDict.items():
					#alreadyFound = 0
					#for eachFileAndRuleID, numProblems in ruleIDIssueDict.items():
					#	if str(eachRuleID) in eachFileAndRuleID and str(eachFileName) in eachFileAndRuleID:
					#		alreadyFound = 1
					#		print("This is good, we found something.")
					#		break
					#if alreadyFound == 0:
					#	combinedFileNameAndRuleID = eachFileName + "\t" + str(eachRuleID)
					#	ruleIDIssueDict[combinedFileNameAndRuleID] = 0
					#	print("filled in a missing value")

		#doneWSonar = subprocess.check_output("mvn clean install -DskipTests=true -Dmaven.test.failure.ignore=true sonar:sonar  -Dsonar.host.url=http://localhost:9000", shell=True)
	except subprocess.CalledProcessError as someError:
		print(someError)
		#sys.exit(0)
		return issueDict
	'''if doneWSonar:
		issues = get_issues()
		if len(issues) < 0:
			print("getting smells failed.")
		#print("Issues: {}".format(issues))
		for eachIssue in issues:
			if eachIssue is not None:
				if eachIssue[2].decode("utf-8") not in alreadyUsedIssues:
					fileName = eachIssue[0].decode("utf-8")
					#print("fileName with an issue: {}".format(fileName))
					if fileName not in issueDict:
						issueDict[fileName] = 1
					else:
						#print("file already in dict! woohoo!")
						issueDict[fileName] += 1
					alreadyUsedIssues[eachIssue[2].decode("utf-8")] = "Used"'''
				#else:
				#	print("HEYYYYYY file already in issues.")
	for eachFile, numIssues in issueDict.items():
		print("issues for {}: {}".format(eachFile, numIssues))
	for eachFileAndRuleID, numIssues in ruleIDIssueDict.items():
		print("{}: {}".format(eachFileAndRuleID, numIssues))
	return issueDict, ruleIDIssueDict

def churn_max(tagTuple, fileSizes, tagTuples, repo):
	print("calculating max churn...")
	commitObj = tagTuple[1]
	churnMaxDict = {}
	version_index = tagTuples.index(tagTuple)
	nextVersionTuple = tagTuples[version_index + 1]
	nextVersionHash = nextVersionTuple[1]
	justFiles = getFilesFromSizes(fileSizes)
	for file in justFiles:
		churnMaxDict[file] = 0
	listOfComHashes = get_list_of_coms_between_versions(commitObj.hexsha, nextVersionHash.hexsha)
	for x in range(0, len(listOfComHashes)-1):
		firstCom = listOfComHashes[x]
		secondCom = listOfComHashes[x+1]
		firstCom = repo.commit(firstCom).hexsha
		secondCom = repo.commit(secondCom).hexsha
		numStatOutput = subprocess.check_output("git diff --numstat {}..{}".format(firstCom, secondCom), shell=True)
		eachFileChanges = numStatOutput.split('\n')
		for eachFileChanged in eachFileChanges:
			changedElements = eachFileChanged.split()
			if len(changedElements) == 3 and ".java" in changedElements[2]:
				#print("changed elements: {}".format(changedElements))
				linesAdded = changedElements[0]
				linesDeleted = changedElements[1]
				fileName = changedElements[2]
				if changedElements[2] not in churnMaxDict:
					churnMaxDict[fileName] = int(changedElements[0]) - int(changedElements[1])
				else:
					oldMaxChurn = churnMaxDict[fileName]
					newMaxChurn = int(changedElements[0]) - int(changedElements[1])
					if newMaxChurn > oldMaxChurn:
						churnMaxDict[fileName] = newMaxChurn
	#for key, maxChurn in churnMaxDict.items():
	#	print("max churn for {}: {}".format(key, maxChurn))
	return churnMaxDict

def loc_added(linesTouchedDict):
	print("calculating lines added...")
	linesAddedDict = {}
	for key, locTuple in linesTouchedDict.items():
		linesAddedDict[key] = locTuple[0]
	return linesAddedDict



def get_list_of_coms_between_versions(firstCommitHash, secondCommitHash):
	listOfComs = []
	commitsBetweenVersions = subprocess.check_output("git log --oneline {}..{}".format(firstCommitHash, secondCommitHash), shell=True)
	listOfCommitsBetweenVersions = commitsBetweenVersions.split('\n')
	for commit in listOfCommitsBetweenVersions:
		commitElements = commit.split()
		if len(commitElements) != 0:
			listOfComs.append(commitElements[0])
	return listOfComs



def getFilesFromSizes(fileSizes):
	justFiles = []
	for item in fileSizes:
		justFiles.append(item[1])
	return justFiles

def get_age(tagTuple, tagTuples, repo):
	print("calculating age...")
	ageDict = {}
	commitObj = tagTuple[1]
	linesTouchedDict = {}
	version_index = tagTuples.index(tagTuple)
	nextVersionTuple = tagTuples[version_index + 1]
	nextVersion = nextVersionTuple[1]
	#print("next version tuple: should end with c92", nextVersion.hexsha)
	previousCommit = subprocess.check_output("git show {}^1".format(nextVersion.hexsha), shell=True)
	previousComHash = previousCommit.split()[1]
	previousCommitDate = subprocess.check_output("git show -s --format=%ci {}".format(previousComHash), shell=True)
	#Date of commit: 2010-03-31 19:35:14 +0000
	previousCommitDate = previousCommitDate.split()[0]
	preComDate = datetime.strptime(previousCommitDate, '%Y-%m-%d')
	#print("Date of commit: {}".format(previousCommitDate))
	#print("previous commit hash of next version: ", previousComHash)
	subprocess.check_output("git checkout -f {}".format(previousComHash), shell=True)
	rawFileData = subprocess.check_output("git ls-tree --full-tree -r {}".format(previousComHash), shell=True)
	splitFiles = rawFileData.split('\n')
	listOfFiles = []
	for fileData in splitFiles:
		fileDataParts = fileData.split()
		if len(fileDataParts) > 3:
			fileName = fileDataParts[3]
			#print("fileName: {}".format(fileName))
			listOfFiles.append(fileName)
	for fileName in listOfFiles:
		if ".java" in fileName:
			try:
				#ageData = subprocess.check_output("git log --follow --format=%aD {} | tail -1".format(fileName), shell=True).rstrip()
				ageData = subprocess.check_output("git log --diff-filter=A --follow --format=%aI -- {} | tail -1".format(fileName), shell=True)
				ageData = ageData[0:10]
				#print("age data: {}".format(ageData))
				fileCreationDate = datetime.strptime(ageData, '%Y-%m-%d')
				#sys.exit(0)
				#Thu, 7 Jun 2007 04:15:32
				#if ageData.endswith(' +0000'):
				#	ageData = ageData[:-6]
				#fileCreationDate = datetime.strptime(ageData, '%a, %d %b %Y %H:%M:%S')
				ageDifference = preComDate - fileCreationDate
				ageDifInWeeks = ageDifference.days / 7
				#print ("age of {}: {} weeks".format(fileName, ageDifInWeeks))
				ageDict[fileName] = abs(ageDifInWeeks)
			except:
				ageDict[fileName] = 0
				continue
	return ageDict

def weighted_age(ageDict, locTouchedDict):
	print("calculating weighted age...")
	weightDict = {}
	for key, locTouched in locTouchedDict.items():
		#print("key: {}".format(key))
		#try:
		if locTouched != 0:
			if key not in ageDict:
				#print("key not in age dict!!!")
				weightDict[key] = 0
			else:
				weightedAge = ageDict[key] / float(locTouched)
				weightDict[key] = weightedAge
				#print("weighted age for {}: {}".format(key, weightedAge))
		else:
			#print("no loc touched for {}".format(key))
			weightDict[key] = 0
		#xcept:
		#	print("something went wrong")
		#	continue
	return weightDict
		

def makeFileNameList(fileDictionaries):
	allFileNames = []
	for eachDict in fileDictionaries:
		for fileName, metric in eachDict.items():
			if fileName not in allFileNames:
				allFileNames.append(fileName)
	return allFileNames


def buildTable(version, sizeDict, smellsDict, churnDict, 
	maxChurnDict, avgChurnDict, chgSetDict, maxChgDict, 
	avgChgDict, locAddedDict, maxLocDict, avgLocDict, 
	numRevDict, numAuthorsDict, ageDict, totTouchedDict, 
	weightedAgeDict, ruleIDIssueDict, ruleIDs):
	print("building table...")
	#print("this ran")
	metricDict = {} #in order of arguments for function
	usedFiles = []
	eachFileDict = []
	eachFileDict.extend((sizeDict, smellsDict, churnDict, 
	maxChurnDict, avgChurnDict, chgSetDict, maxChgDict, 
	avgChgDict, locAddedDict, maxLocDict, avgLocDict, 
	numRevDict, numAuthorsDict, ageDict, totTouchedDict, 
	weightedAgeDict))
	allFileNames = makeFileNameList(eachFileDict)
	for fileName, smellNum in smellsDict.items():
		print("smells for {}: {}".format(smellNum, fileName))
	#print("lenght of file dict: {}".format(len(eachFileDict)))
	#print("total file names for version: {}".format(len(allFileNames)))
	for fileName in allFileNames:
		if fileName not in metricDict:
			metricDict[fileName] = [fileName, version]
	for x in range(0, len(eachFileDict)): 
		singleMetricDictionary = eachFileDict[x]#fileDictionary in eachFileDict:
		filesForThisMetric = []
		for fileName, metric in singleMetricDictionary.items():
			alreadyFound = 0
			for existingFileName, listOfMetrics in metricDict.items():
				if alreadyFound == 0:
					if fileName in existingFileName:
						if fileName not in usedFiles:
							usedFiles.append(fileName)
						filesForThisMetric.append(fileName)
						#print("matched {} with existing file {}".format(fileName, existingFileName))
						metricDict[existingFileName].append(metric)
						alreadyFound = 1
		for eachIndFileName in usedFiles:
			if eachIndFileName not in filesForThisMetric:
				print("added 0 for {}".format(eachIndFileName))
				metricDict[eachIndFileName].append(0)
	for existingFileName in metricDict.keys():
		if ".java" in existingFileName:
			#print(existingFileName)
			ruleIDsForSpecificFile = [x for x in ruleIDIssueDict.keys() if existingFileName in x]
			splitUpFileNameAndIDs = [y.split("\t") for y in ruleIDsForSpecificFile]
			splitUpFileNameAndIDs = sorted(splitUpFileNameAndIDs, key=lambda x: int(x[1]))
			for eachThingy in splitUpFileNameAndIDs:
				#print("{}...{}".format(eachThingy[0], eachThingy[1]))
				combinedAgain = eachThingy[0] + "\t" + eachThingy[1]
				numTimesRuleBroken = ruleIDIssueDict[combinedAgain]
				if numTimesRuleBroken != 0:
					print("rule {} for file {} has been broken {} times".format(eachThingy[1], eachThingy[0], numTimesRuleBroken))
				metricDict[eachThingy[0]].append(numTimesRuleBroken)
	#sys.exit(0)
			#theCount = 0
			#for ruleIDFileKey in ruleIDIssueDict.keys():
			#	if existingFileName in ruleIDFileKey:
			#		theCount += 1
			#print("the count: {}".format(theCount))

	'''for x in range(0, len(ruleIDs)):
		for fileNameAndRuleID, numIssues in ruleIDIssueDict.items():
			alreadyFound = 0
			nameAndRuleList = fileNameAndRuleID.split('\t')
			fileNameToFind = nameAndRuleList[0]
			ruleID = nameAndRuleList[1]
			#print("File name: {}".format(fileNameToFind))
			#print("Rule ID: {}".format(ruleID))
			if int(ruleID) == int(ruleIDs[x]):
				#print("matched rule id {} up".format(ruleID))
				for existingFileName, listOfMetrics in metricDict.items():
					if alreadyFound == 0:
						if fileNameToFind in existingFileName:
							print("found a match for {} on rule id {}".format(fileNameToFind, ruleID))
							metricDict[existingFileName].append(numIssues)
							alreadyFound = 1'''
	#print("info on src/java/org/apache/jcs/engine/control/CompositeCache.java: {}".format(totTouchedDict["src/java/org/apache/jcs/engine/control/CompositeCache.java"]))
	with open("ddmTable.csv", "a") as csv_file:
		wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
		for fileName, metricList in metricDict.items():
			print("length of row: {}".format(len(metricList)))
			if ".java" in fileName and len(metricList) == 310 and metricList[2] > 0:#len(metricList) == 18 and metricList[2] > 0:
				wr.writerow(metricDict[fileName])

def createCSVHeader(ruleIDs):
	metricNames = ["File Name", "Version", "Size", "Number of Smells", "Churn", 
		"Max Churn", "Avg Churn", "Chg Set Size", "Max Chg Set Size",
		"Avg Chg Set Size", "LOC Added", "MAX LOC Added", "AVG LOC Added",
		"Number of Revisions", "Number of Authors", "Age in Weeks",
		"Total Lines Touched", "Weighted Age"]
	print(ruleIDs)
	for eachRuleID in ruleIDs:
		#print("another rule id")
		metricNames.append(eachRuleID)
	metricNames.append("Defective")
	with open("ddmTable.csv", "wb") as csv_file:
		wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
		wr.writerow(metricNames)
		cwd = os.getcwd()
		print("Printed metric names...")
		print("working directory: {}".format(cwd))
		#sys.exit(0)



def createSizeDict(fileSizes):
	#(tagName, fileName, linesOfCode))
	fileSizeDict = {}
	for item in fileSizes:
		if item[1] not in fileSizeDict:
			fileSizeDict[item[1]] = item[2]
	return fileSizeDict


def getTotalIssues(jiraInstance):
	block_size = 150
	block_num = 0
	totalIssues = []
	while True:
		start_idx = block_num*block_size
		issues = jiraInstance.search_issues('project = ' + sys.argv[2] + ' AND issuetype = "Bug" AND status in (Resolved, Closed) ORDER BY resolved ASC', start_idx, block_size)
		for issue in issues:
			totalIssues.append(issue)
		#totalIssues.append(issues)
		if len(issues) == 0:
		# Retrieve issues until there are no more to come
			break
		block_num += 1
	return totalIssues

def getBugs(jiraURL, repo):
	print("calculating bugs...")
	versionFileBugDict = {}
	commitHashRegex = r'\b([a-f0-9]{40})\b'
	#Regex to extract the Author of the commit from commit messages
	commitAuthorRegex = r'Author: ([ a-zA-Z]*)'
	comHashHist = r'commit ([a-zA-Z0-9]*)'
	allCommitsList = subprocess.check_output("git log --all --oneline", shell=True).split('\n')
	#print("total commits: {}".format(len(allCommitsList)))
	#Sets Jira instance in order to gather requirements from
	jira = JIRA(jiraURL)
	totalIssues = getTotalIssues(jira)
	#print("Total issues: {}".format(len(totalIssues)))
	for eachIssue in totalIssues:
		try:
			issueName = eachIssue.key.encode('utf-8').strip()
			matchingCommits = [s for s in allCommitsList if issueName in s]
			if len(matchingCommits) != 0:
				#print("what am I doing: {}".format(matchingCommits[0].split()[0]))
				fullCommitInstances = [repo.commit(x.split()[0]) for x in matchingCommits]
				fullCommitInstances = sorted(fullCommitInstances, key=lambda x: x.committed_date)
				firstRelCom = fullCommitInstances[0]
				#print("for commit {}:".format(firstRelCom.hexsha))
				dateOfCommit = datetime.fromtimestamp(firstRelCom.committed_date).strftime('%Y-%m-%d')
				difference = subprocess.check_output("git diff -U0 {}^ {} | ../../bashScript.sh".format(firstRelCom.hexsha, firstRelCom.hexsha), shell=True)
				linesChanged = difference.split('\n')
				linesChanged = [x.split(":") for x in linesChanged if ".java" in x]
				linesChanged = [(x[0], x[1]) for x in linesChanged if len(x) > 1]
				fileAndLines = []
				currentFileName = "no file yet"
				firstLineChanged = -1
				currentLine = -1
				for fileAndLineTuple in linesChanged:
					#print("file and line: {}".format(fileAndLineTuple))
					if currentFileName == "no file yet":
						currentFileName = fileAndLineTuple[0]
						firstLineChanged = fileAndLineTuple[1]
						currentLine = fileAndLineTuple[1]
					else:
						if fileAndLineTuple[0] == currentFileName:
							currentLine = fileAndLineTuple[1]
						else:
							fileAndLines.append((currentFileName, firstLineChanged, currentLine))
							currentFileName = fileAndLineTuple[0]
							firstLineChanged = fileAndLineTuple[1]
							currentLine = fileAndLineTuple[1]
				if firstLineChanged != -1:
					fileAndLines.append((currentFileName, firstLineChanged, currentLine))
				for fileTuple in fileAndLines:
					#print("file Tuple: {}".format(fileTuple))
					previousChanges = []
					try:
						#previousChanges = subprocess.check_output("git blame -L{},+{} {}^ -- {}".format(fileTuple[1], int(fileTuple[2]) - int(fileTuple[1]), firstRelCom.hexsha, fileTuple[0]), shell=True).split('\n')
						p = subprocess.Popen(["git",  "blame",  "-L{},+{}".format(fileTuple[1], int(fileTuple[2]) - int(fileTuple[1])), "{}^".format(firstRelCom.hexsha), "--", "{}".format(fileTuple[0])], stdout=PIPE, stderr=PIPE)
						output, error = p.communicate()
						#print("output: {}".format(str(output)))
						if p.returncode != 0: 
							#print("thing failed %d %s %s" % (p.returncode, output, error))
							numbers = [int(s) for s in str(error).split() if s.isdigit()]
							if len(numbers) > 0:
								maxLines = numbers[len(numbers)-1]
								#print("max lines: {}".format(maxLines))
								previousChanges = subprocess.check_output("git blame -L{},+{} {}^ -- {}".format(fileTuple[1], maxLines - int(fileTuple[2]) - 1, firstRelCom.hexsha, fileTuple[0]), shell=True).split('\n')
								#print("ran max lines successfully.")
						else:
							previousChanges = str(output).split('\n')
					except subprocess.CalledProcessError as someError:
						#print("here is the exact error: |||{}|||".format(someError))
						try:
							previousChanges = subprocess.check_output("git blame -L{},+{} {}^ -- {}".format(fileTuple[1], 1, firstRelCom.hexsha, fileTuple[0]), shell=True).split('\n')
						except:
							continue

					foundBugCommits = []
					for eachLineChange in previousChanges:
						lineChangedParts = eachLineChange.split()
						if len(lineChangedParts) > 0:
							lineChangedComHash = lineChangedParts[0]
							if lineChangedComHash not in foundBugCommits:
								try:
									foundBugCommits.append(lineChangedComHash)
									#print("old commit: {}".format(lineChangedComHash))
									lineChangedCommitObj = repo.commit(lineChangedComHash)
									correspondingTag = subprocess.check_output("git describe --contains {}".format(lineChangedCommitObj.hexsha), shell=True)
									#print("corresponding tag: {}".format(correspondingTag)).split('~')[0]
									if (correspondingTag, fileTuple[0]) in versionFileBugDict:
										versionFileBugDict[(correspondingTag.split('~')[0], fileTuple[0])] += 1
									else:
										versionFileBugDict[(correspondingTag.split('~')[0], fileTuple[0])] = 1
								except:
									print("continuing...")
		except subprocess.CalledProcessError as UnknownErr:
			print("...")
	#for tupleKey, value in versionFileBugDict.items():
	#	print("num bugs for {}: {}".format(tupleKey, value))
	return versionFileBugDict


def addBugsToCSV(versionFileBugDict):
	newMetricRows = []
	with open("ddmTable.csv") as csv_file:
		readCSV = csv.reader(csv_file, delimiter=',')
		rowOneHandled = 0
		for row in readCSV:
			foundMatch = 0
			for tupleKey, value in versionFileBugDict.items():
				if tupleKey[0] == row[1] and tupleKey[1] == row[0]:#in row and tupleKey[1] in row:
					if foundMatch == 1:
						row[len(row)-1] = "Yes"
					else:
						#print("got a match")
						foundMatch = 1
						row.append("Yes")
			if foundMatch == 0:
				if rowOneHandled == 0:
					rowOneHandled = 1
				else:
					row.append("No")
			newMetricRows.append(row)
	with open("ddmTable.csv", "wb") as csv_file:
		wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
		for eachRow in newMetricRows:
			wr.writerow(eachRow)

def resetSonarDB():
	print("nothing so far.")

def createRepo(githubURL):
	continuedPath = ""
	try:
		os.makedirs("repoHolder")
	except OSError as e:
		if e.errno != errno.EEXIST:
			raise
		else:
			shutil.rmtree("./repoHolder")
			os.makedirs("repoHolder")
	git.Git("./repoHolder").clone(githubURL)
	for x in os.listdir('./repoHolder'):
		print("this is something: {}".format(str(x)))
		if os.path.isdir(os.path.join('./repoHolder', x)):
			print("folder within repoHolder: {}".format(str(x)))
			continuedPath = str(x)
		else:
			print("not recognized as a directory... {}".format(str(x)))
	return continuedPath


def main():
	githubURL = sys.argv[1]
	continuedPath = createRepo(githubURL)
	projectPath = "./repoHolder/{}".format(continuedPath)#sys.argv[1]
	jiraURL = sys.argv[3]
	initialFolder = os.path.abspath(os.curdir)
	repo = getRepo(projectPath)
	#print("initial folder: ", initialFolder)
	#print("project path: ")
	tagTuples = getReleases(projectPath, repo)
	ruleIDs = get_rule_IDs()
	#for item in tagTuples:
	#	print("tuple: ", item)
	#fileSizes = sizeAtBeginningOfRelease(tagTuples[23])
	#for item in fileSizes:
	#		print(item)
	#get_smells(tagTuples[7], fileSizes, tagTuples, repo)
	#sys.exit(0)
	#runSonar(tagTuples[7])
	print("length of tag tuples: {}".format(len(tagTuples)))
	createCSVHeader(ruleIDs)
	for x in range(0, len(tagTuples)-1):
		resetSonarDB()
		fileSizes = sizeAtBeginningOfRelease(tagTuples[x])
		sizeDict = createSizeDict(fileSizes)
		smellsDict, ruleIDIssueDict = get_smells(tagTuples[x], fileSizes, tagTuples, repo, ruleIDs)
		linesTouchedDict = loc_touched(tagTuples[x], fileSizes, tagTuples, repo) #file dict, tuple of added and deleted
		churnDict = churn(linesTouchedDict) #file dictionary, churn of files
		maxChurnDict = churn_max(tagTuples[x], fileSizes, tagTuples, repo) #file dictionary, max of churn for a single commit
		avgChurnDict = churn_avg(tagTuples[x], fileSizes, tagTuples, repo) #file dictionary, avg of churn for each time file was touched
		chgSetDict = chg_set_size(tagTuples[x], fileSizes, tagTuples, repo) #file dictionary, total number of associated files
		maxChgDict = max_chg_set(tagTuples[x], fileSizes, tagTuples, repo) #file dictionary, max # of associated files for a revision
		avgChgDict = avg_chg_set(tagTuples[x], fileSizes, tagTuples, repo) #file dictionary, avg associated files for each revision
		locAddedDict = loc_added(linesTouchedDict) #file dictionary, sum of loc added
		maxLocDict = loc_max(tagTuples[x], fileSizes, tagTuples, repo) #file dictionary, max added
		avgLocDict = loc_avg(tagTuples[x], fileSizes, tagTuples, repo) #file dictionary, tuple of added/deleted
		numRevDict = num_revisions(tagTuples[x], fileSizes, tagTuples, repo) #file dictionary, num revisions
		numAuthorsDict = num_authors(tagTuples[x], fileSizes, tagTuples, repo)  #file dictionary, num authors per file
		ageDict = get_age(tagTuples[x], tagTuples, repo) #file dictionary, age in weeks
		totTouchedDict = total_loc_touched(linesTouchedDict) #file dict, total Lines touched
		weightedAgeDict = weighted_age(ageDict, totTouchedDict) #file dict, weighted age
		buildTable(tagTuples[x][0], sizeDict, smellsDict, churnDict, maxChurnDict, avgChurnDict, chgSetDict, maxChgDict, avgChgDict, locAddedDict, maxLocDict, avgLocDict, numRevDict, numAuthorsDict, ageDict, totTouchedDict, weightedAgeDict, ruleIDIssueDict, ruleIDs)
	versionFileBugDict = getBugs(jiraURL, repo)
	addBugsToCSV(versionFileBugDict)


if __name__ == '__main__':
	main()
