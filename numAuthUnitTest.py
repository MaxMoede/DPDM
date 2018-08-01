#MAX MOEDE
from jira import JIRA
from git import Repo
import multiprocessing
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



def get_list_of_coms_between_versions():
	firstCommitHash = "0.2"
	secondCommitHash = "0.2-rc1"
	listOfComs = []
	commitsBetweenVersions = subprocess.check_output("git log --oneline {}..{}".format(firstCommitHash, secondCommitHash), shell=True)
	listOfCommitsBetweenVersions = commitsBetweenVersions.split('\n')
	for commit in listOfCommitsBetweenVersions:
		commitElements = commit.split()
		if len(commitElements) != 0:
			listOfComs.append(commitElements[0])
	return listOfComs



def num_authors(tagTuple, fileSizes, tagTuples, repo): #calculates the number of authors for a file within a release period
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


def main():
	os.chdir("repoHolder/tika")
	listOfComs = get_list_of_coms_between_versions()
	print("length of list of coms: {}".format(len(listOfComs)))


if __name__ == '__main__':
	main()
