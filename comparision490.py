from pymarc import *
import json


def checkForBreak():
    """just checks if the function should break or not"""
    goOn = 't'
    goOn = input('Do you want to continue or break? Enter "n" to break. \n')

    if goOn == 'n':
        print('breaking!')
        return True
    else:
        return False
# open the local records
def marc490(filename):
    marcFile = str(filename)

    recordCounter = 0

    recDict = {}
    with open(marcFile, 'rb') as fh:
        reader = MARCReader(fh, to_unicode=True, force_utf8=True)

        for rec in reader:
            # return rec
            # print(rec.leader)

#           checks to see if an OCLC 035 exists and if so, strips the prefix and removes leading integers before
#           returning the dictionary of the MARC with the integer key

            try:
                if rec['035']['a'] is None:
                    continue
                elif '(OCoLC)' in rec['035']['a']:
                        tempKey = rec['035']['a']
                        tempKey = tempKey.strip('(OCoLC)')
                        tempKey = int(tempKey)
                        # print(tempKey)
                        recDict[tempKey] = rec.as_dict()
            except (TypeError, ValueError):
                print(rec['001'], 'failed')

            # print(recDict[rec['035']['a'].strip('(OCoLC)')])

            goOn = 't'
            # goOn = input('continue?')
            if goOn == 'n':
                return recDict

        return recDict

def returnKeyList(marcDict):
    """returns a list of keys of the dictionary for use"""

    keyList = []
    for a in marcDict:
        if a is None:
            continue
        # elif '(OCoLC)' in a:
        try:
            # keyList.append(int(a.strip('(OCoLC)')))
            keyList.append(a)
        except TypeError:
            print('appending: ', a, 'failed due to TypeError')

# This section for debugging
        goOn = 'f'
        # goOn = (input('continue?:\n'))
        if goOn == 'n':
            return keyList

    return keyList

def compareKeyList(localList, masterList):
    """compares the keys in the local list to the master list to return an actionable list of records in both"""
    keysInLocalandMaster = []

    for a in localList:
        if a in masterList:
            keysInLocalandMaster.append(a)

    return keysInLocalandMaster

def compareKeyNotInList(localList, masterList):
    """compares the keys in the local list to the master list to return an actionable list of records in both"""
    keysInLocalandNotMaster = []

    for a in localList:
        if a not in masterList:
            keysInLocalandNotMaster.append(a)

    return keysInLocalandNotMaster

def getDictKey(dict):
    """returns key of the dictionary"""
    dictKey = ''
    for d in dict:
        # print(d)
        for key in d:
            # print(key)
            dictKey = str(key)
        # print (dictKey)

    return dictKey

def getSubfieldList(dict, dictKey):

    subfieldList = []
    for ser in dict:
        for subfield in ser[dictKey]['subfields']:
            for key in subfield:
                # print(key)
                if key not in subfieldList:
                    subfieldList.append(key)
    # print('subfieldList is: ', subfieldList)
    return subfieldList

def extractCompare(partDict, masterDict):

    masterDictKey = getDictKey(masterDict)
    masterDictSubfieldList = getSubfieldList(masterDict, masterDictKey)

    match = False

    for series in masterDict:
        tempMasterDict = {}
        for dict in series[masterDictKey]['subfields']:
            # print('testSeries = ', partDict, 'compared to: ', dict)

            for key in masterDictSubfieldList:
                try:
                    if key != '5':
                        # print(key, dict[key])
                        tempMasterDict[key] = dict[key]
                except KeyError:
                    pass
        print('testSeries = ', partDict, 'compared to: ', tempMasterDict)
        if tempMasterDict == partDict:
            match = True

    return match

def simpleCompare(localDict, MasterDict):
    """does a simple comparisions between provided dictionary of local records for a given tag to those in the same
    same tag for the master record"""

    keyInDict = getDictKey(localDict)

    print('keyInDict is: ', keyInDict)

    subfieldList = getSubfieldList(localDict, keyInDict)

    compDict = {}
    for ser in localDict:
        for dict in ser[keyInDict]['subfields']:
            # print(dict)
            for key in subfieldList:
                try:
                    if key != '5':
                        # print(key, dict[key])
                        compDict[key] = dict[key]
                except KeyError:
                    pass
        seriesInMaster = extractCompare(compDict, MasterDict)
        print(compDict, seriesInMaster)


        stop = checkForBreak()
        if stop:
            return

def getTags(keyDict, tagID):
    """replaces getTagValues by getting the entire set of data for a given tag"""

    keyDict = keyDict['fields']
    resultTagValue = []
    tagValue = None

    tagList = []
    for f in keyDict:
        tagList.append(f)

    if tagList is None:
        return resultTagValue

    for lines in tagList:
        # print(lines)
        for tag in lines:
            # print(tag)
            if tag == tagID:
                # print('true!')
                resultTagValue.append(lines)

    return resultTagValue

def getTagValues(keyDict, tagID, subfield):
    """as an experiment, returns the OCLC Number in the local record and the Master Record"""

    keyDict = keyDict['fields']
    tagValue = None
    resultTagValue = None

    # tagID = '035'
    # subfield = 'a'

    for tagDict in keyDict:
        for tag in tagDict:
            if tag == tagID:
                tagValue = tagDict
    # print('step 1:', tagValue)
    if tagValue is None:
        return resultTagValue


    # print(oclcValue)

    if subfield is None:
        for tags in tagValue:
            # print (tags)
            if tags == tagID:
                # print('found!')
                resultTagValue = tagValue[tagID]
    else:
        tagValue = tagValue[tagID]['subfields']
        for sfdict in tagValue:
            for sf in sfdict:
                if sf == subfield:
                    # print('true!')
                    # print(sfdict[subfield])
                    resultTagValue = sfdict[subfield]

    return resultTagValue

def logResult(recordKey, logString):

    testinglogFile = 'testinglogFile.txt'
    with open(testinglogFile, 'a') as log:
        try:
            log.write('\n'+logString+'\n')
        except UnicodeEncodeError:
            log.write('\n'+'failed to write record key: '+str(recordKey)+'\n')

def stringFormDict(tagSet):
    """given a tag set in dictionary form, returns the strings ready for printing"""

    tagSetStr = ''
    lenTS = len(tagSet)
    # print(lenTS)
    tsCounter = 0
    for line in tagSet:
        tagSetStr = tagSetStr+json.dumps(line)
        tsCounter += 1
        if tsCounter < lenTS:
            tagSetStr = tagSetStr+'\n\t\t'
        # print(tsCounter)

    return tagSetStr

def doSomething():

# Create dictionaries from the local and master marc files
    print('\nbuilding dictionaries...')
    lDict = marc490('10k.mrc')
    mDict = marc490('490OCLC.mrc')
    print('... DONE!')

# Gets list of keys from the 2 dictionaries, and a third list of common keys
    print('\nbuilding lists...')
    lKeys = returnKeyList(lDict)
    mKeys = returnKeyList(mDict)
    aKeys = compareKeyList(lKeys, mKeys)
    print('... DONE!')

# return, for comparison the two OCLC numbers in the records
    print('\ncomparing results and writing to log')
    keyCounter = 0
    for key in aKeys:
        lSysNumber = getTagValues(lDict[key], '001', None)
        oclcNumberL = getTagValues(lDict[key], '035', 'a')
        oclcNumberM = getTagValues(mDict[key], '035', 'a')
        local260a = getTagValues(lDict[key], '260', 'a')
        master260a = getTagValues(mDict[key], '260', 'a')
        local440 = getTags(lDict[key], '440')
        local440st = stringFormDict(local440)
        master440 = getTags(mDict[key], '440')
        master440st = stringFormDict(master440)

        local490 = getTags(lDict[key], '490')
        local490st = stringFormDict(local490)
        master490 = getTags(mDict[key], '490')
        master490st = stringFormDict(master490)

        local830 = getTags(lDict[key], '830')
        local830st = stringFormDict(local830)
        master830 = getTags(mDict[key], '830')
        master830st = stringFormDict(master830)

        logString = 'List#: '+str(keyCounter)+'\nKey: '+str(key)+'\n\tLocal Sys#: '+str(lSysNumber)
        logString = logString+'\n\tOCLC Numbers:\n\t\tLocal: '+str(oclcNumberL)+'\n\t\tMaster: '+str(oclcNumberM)
        logString = logString+'\n\tImprint (260):\n\t\tLocal :'+str(local260a)+'\n\t\tMaster: '+str(master260a)
        logString = logString+'\n\tSeries(440): \n\t\tLocal: \n\t\t'+local440st+'\n\t\tMaster: \n\t\t'+master440st
        logString = logString+'\n\tSeries(490):\n\t\tLocal: \n\t\t'+local490st+'\n\t\tMaster: \n\t\t'+master490st
        logString = logString+'\n\tSeries(830):\n\t\tLocal: \n\t\t'+local830st+'\n\t\tMaster: \n\t\t'+master830st

        logResult(str(keyCounter), logString)

        # try:
        #     print('List#: '+str(keyCounter) +
        #           '\nKey: '+str(key)+'\n\tLocal Sys#: '+str(lSysNumber) +
        #           '\n\tOCLC Numbers:\n\t\tLocal:'+str(oclcNumberL)+'\n\t\tMaster'+str(oclcNumberM)+'\n' +
        #           '\n\tImprint (260):\n\t\tLocal:'+str(local260a)+'\n\t\tMaster'+str(master260a)+'\n'
        #           )
        # except UnicodeEncodeError:
        #     print('List#: '+str(keyCounter)+' had error in writing')

        goOn = 't'
        # goOn = input('Continue? To stop enter "n"\n')
        if goOn == 'n':
            break

        keyCounter += 1
    print('... DONE!')








