#MAX MOEDE
#RUN WITH PYTHON 3.4+ BECAUSE OF STATISTICS IMPORT
import csv
import sys
import statistics



def get_rows_without_individual_smell_data(fileName):
	theRows = []
	firstRowRead = 0
	with open(fileName, 'r') as csvfile:
		tableReader = csv.reader(csvfile, delimiter=',')
		for row in tableReader:
			if firstRowRead == 0:
				firstRowRead = 1
				continue
			#print("This is a row: {}".format(row))
			allMetrics = row[:18]
			allMetrics.append(row[len(row)-1])
			#print("This is now the row: {}".format(allMetrics))
			theRows.append(allMetrics)
	return theRows

def compute_avgs(sizes, smells, churns, maxChurns, avgChurns, chgSetSizes, maxChgSets, 
				avgChgSets, locAddeds, maxLocs, avgLocs, numRevisions, numAuthors, ages, linesTouched,
				weightedAges, defectives, totalRows, numberOfReleases, dataSetName):
	firstCSVLine = ["Dataset Name", "Num Releases", "Total Rows", "Sizes_AVG", "Sizes_STDV", 
					"Smells_AVG", "Smells_STDV", "Churn_AVG", "Churn_STDV", "MaxChurn_AVG", "MaxChurn_STDV",
					"AvgChurn_AVG", "AvgChurn_STDV", "ChgSetSize_AVG", "ChgSetSize_STDV", "MaxChgSetSize_AVG",
					"MaxChgSetSize_STDV", "AvgChgSetSize_AVG", "AvgChgSetSize_STDV", "LocAdded_AVG", 
					"LocAdded_STDV", "MaxLocAdded_AVG", "MaxLocAdded_STDV", "AVGLocAdded_AVG", "AVGLocAdded_STDV",
					"NumRevisions_AVG", "NumRevisions_STDV", "NumAuthors_AVG", "NumAuthors_STDV",
					"Age_AVG", "Age_STDV", "LinesTouched_AVG", "LinesTouched_STDV", "WeightedAges_AVG",
					"WeightedAges_STDV", "DefectiveRate_AVG", "DefectiveRate_STDV"]
	theFullMetricList = []
	intDefectives = []
	sizesAvg = statistics.mean(sizes)
	sizesStd = statistics.pstdev(sizes)
	print("Size avg: {}".format(sizesAvg))
	print("Size std: {}".format(sizesStd))
	smellsAvg = statistics.mean(smells)
	smellsStd = statistics.pstdev(smells)
	print("Smells avg: {}".format(smellsAvg))
	print("Smells std: {}".format(smellsStd))
	churnAvg = statistics.mean(churns)
	churnStd = statistics.pstdev(churns)
	maxChurnsAvg = statistics.mean(maxChurns)
	maxChurnsStd = statistics.pstdev(maxChurns)
	avgChurnsAvg = statistics.mean(avgChurns)
	avgChurnsStd = statistics.pstdev(avgChurns)
	chgSetSizesAvg = statistics.mean(chgSetSizes)
	chgSetSizesStd = statistics.pstdev(chgSetSizes)
	maxChgSetsAvg = statistics.mean(maxChgSets)
	maxChgSetsStd = statistics.pstdev(maxChgSets)
	avgChgSetsAvg = statistics.mean(avgChgSets)
	avgChgSetsStd = statistics.pstdev(avgChgSets)
	locAddedsAvg = statistics.mean(locAddeds)
	locAddedsStd = statistics.pstdev(locAddeds)
	maxLocsAvg = statistics.mean(maxLocs)
	maxLocsStd = statistics.pstdev(maxLocs)
	avgLocsAvg = statistics.mean(avgLocs)
	avgLocsStd = statistics.pstdev(avgLocs)
	numRevisionsAvg = statistics.mean(numRevisions)
	numRevisionsStd = statistics.pstdev(numRevisions)
	numAuthorsAvg = statistics.mean(numAuthors)
	numAuthorsStd = statistics.pstdev(numAuthors)
	agesAvg = statistics.mean(ages)
	agesStd = statistics.pstdev(ages)
	linesTouchedAvg = statistics.mean(linesTouched)
	linesTouchedStd = statistics.pstdev(linesTouched)
	weightedAgesAvg = statistics.mean(weightedAges)
	weightedAgesStd = statistics.pstdev(weightedAges)
	for eachItem in defectives:
		if eachItem == "No":
			intDefectives.append(0)
		elif eachItem == "Yes":
			intDefectives.append(1)
		else:
			print("we have an issue. eachItem: {}".format(eachItem))
			sys.exit(0)
	defectiveAvg = statistics.mean(intDefectives)
	defectiveStd = statistics.pstdev(intDefectives)
	theFullMetricList.extend(dataSetName, numberOfReleases, totalRows, sizesAvg, sizesStd, smellsAvg, smellsStd,
							churnAvg, churnStd, maxChurnsAvg, maxChurnsStd, avgChurnsAvg, avgChurnsStd, 
							chgSetSizesAvg, chgSetSizesStd, maxChgSetsAvg, maxChgSetsStd, #Finish here)
	

def organize_into_sections(theRows, dataSetName):
	totalRows = len(theRows)
	sizes = []
	releases = []
	smells = []
	churns = []
	maxChurns = []
	avgChurns = []
	chgSetSizes = []
	maxChgSets = []
	avgChgSets = []
	locAddeds = []
	maxLocs = []
	avgLocs = []
	numRevisions = []
	numAuthors = []
	ages = []
	linesTouched = []
	weightedAges = []
	defectives = []
	print("hi")
	print("doing sanity check:")
	print("Each row should have 19 things in it")
	for eachRow in theRows:
		if eachRow[1] not in releases:
			releases.append(eachRow[1])
		sizes.append(float(eachRow[2]))
		smells.append(float(eachRow[3]))
		churns.append(float(eachRow[4]))
		maxChurns.append(float(eachRow[5]))
		avgChurns.append(float(eachRow[6]))
		chgSetSizes.append(float(eachRow[7]))
		maxChgSets.append(float(eachRow[8]))
		avgChgSets.append(float(eachRow[9]))
		locAddeds.append(float(eachRow[10]))
		maxLocs.append(float(eachRow[11]))
		avgLocs.append(float(eachRow[12]))
		numRevisions.append(float(eachRow[13]))
		numAuthors.append(float(eachRow[14]))
		ages.append(float(eachRow[15]))
		linesTouched.append(float(eachRow[16]))
		weightedAges.append(float(eachRow[17]))
		defectives.append(eachRow[18])
	print("number of analyzed releases: {}".format(len(releases)))
	numberOfReleases = len(releases)
	compute_avgs(sizes, smells, churns, maxChurns, avgChurns, chgSetSizes, maxChgSets, 
				avgChgSets, locAddeds, maxLocs, avgLocs, numRevisions, numAuthors, ages, linesTouched,
				weightedAges, defectives, totalRows, numberOfReleases, dataSetName)



def main():
	dataSetName = sys.argv[2]
	allTheRows = get_rows_without_individual_smell_data(sys.argv[1])
	organize_into_sections(allTheRows, dataSetName)

if __name__ == '__main__':
	main()