from pymarc import *
import json
import time
import csv

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

def dictValStrip(dictVal):
    """Strips the specified strings/characters prior to comparison. Note that the order matters because if you strip the
    leading spaces prior to the words with trailing spaces, it won't find the words."""

    r = ['the ', 'A ', 'a ', 'The ', ';', ' ', ',', '.', '[', ']']

    dictVal = dictVal
    for thing in r:
        dictVal = dictVal.replace(thing, '')

    return dictVal

def stringValStrip(listString):
    arts = ['the', 'a', 'an', 'el', 'los', 'la', 'las', 'un', 'unos', 'una', 'unas', 'le', 'la', 'l’', 'les', 'un',
            'une', 'des']

    punct = [';', ' ', ',', '.', '[', ']', '<', '>', '|']


    afterListItem = []
    for listItem in listString:
        tempafterListItem = []
        #replace articles from list arts, split each word into the list and see if that word is in the arts list - if so remove it, then recomplile into a string.
        llist = listItem.split(' ')
        # print(llist)
        for w in llist:
            if w == 'v:':
                break
            if w not in arts and w not in punct:
                tempafterListItem.append(w)
        # print(tempafterListItem)

        # input('paused')

        # for word in tempafterListItem:
        #     if word in arts or word in punct:
        #         print("found ", word)
        #         tempafterListItem.remove(word)
        #     # if word in punct:
        #     #     tempafterListItem.remove(word)

        stTempAfterListItem = " ".join(tempafterListItem)

        afterListItem.append(stTempAfterListItem)

    return afterListItem

def returnFormat(dict):

    # extract the code from the 008 23 values
    formatCode = 'None'
    for tag in dict['fields']:
        for k in tag:
            if k == '008':
                formatCode = tag[k][23:24]

    format = ''
    if formatCode in ['s', 'o', 'q']:
        format = 'electronic'
    elif formatCode in [' ', 'r', 'd']:
        format = 'print'
    elif formatCode in ['a', 'b', 'c']:
        format = 'microform'
    else:
        format = 'unknown'

    return format

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
                        dictVal = dictValStrip(dict[key])
                        tempMasterDict[key] = dictVal
                except KeyError:
                    pass
        # print('testSeries = testSeries', partDict, 'compared to: ', tempMasterDict)
        if tempMasterDict == partDict:
            match = True

    return match

def simpleCompare(localDict, MasterDict):
    """does a simple comparisions between provided dictionary of local records for a given tag to those in the same
    same tag for the master record"""

    keyInDict = getDictKey(localDict)

    # print('keyInDict is: ', keyInDict)

    subfieldList = getSubfieldList(localDict, keyInDict)
    compareresultList = []
    compDict = {}
    for ser in localDict:
        for dict in ser[keyInDict]['subfields']:
            # print(dict)
            for key in subfieldList:
                try:
                    if key != '5':
                        # print(key, dict[key])
                        dictVal = dictValStrip(dict[key])
                        compDict[key] = dictVal
                except KeyError:
                    pass
        seriesInMaster = extractCompare(compDict, MasterDict)
        # print(compDict, seriesInMaster)
        result = []
        result.append(str(compDict))
        result.append(seriesInMaster)
        # result = str(compDict)+' '+str(seriesInMaster)
        compareresultList.append(result)
    return compareresultList


        # stop = checkForBreak()
        # if stop:
        #     return

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

def logStartEnd(now):
    testinglogFile = 'testinglogFile.txt'
    with open(testinglogFile, 'a') as log:
        try:
            log.write(now)
        except UnicodeEncodeError:
            log.write('\n'+'failed to write record key: '+str(recordKey)+'\n')

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

def runComparison():

    now = time.strftime('%Y-%m-%d %H:%M:%S')
    now = 'starting at: '+str(now)
    logStartEnd(now)
    print(now)


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

        # Return Formats
        lFormat = returnFormat(lDict[key])
        mFormat = returnFormat(mDict[key])
        matchFormat = False
        if lFormat == mFormat:
            if lFormat.upper() == "UNKNOWN":
                lFormat = "Unknown"
            else:
                matchFormat = True

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

        # compare local 440 to master 830
        compareResult = simpleCompare(local440, master830)
        compareResult1 = []
        if compareResult is None or len(compareResult) == 0:
            compResult = 'None'
        else:
            compResult = ''
            for r in compareResult:
                compareResult1.append(str(r[0])+' '+str(r[1]))

            for c in compareResult1:
                compResult = compResult+c+'\n\t\t'
        # print(compareResult)

        logString = 'List#: '+str(keyCounter)+'\nKey: '+str(key)+'\n\tLocal Sys#: '+str(lSysNumber)

        # add oclc numbers
        logString = logString+'\n\tOCLC Numbers:\n\t\tLocal: '+str(oclcNumberL)+'\n\t\tMaster: '+str(oclcNumberM)

        # add formats
        logString = logString+'\n\tFormats (008 23): Formats Match?: '+str(matchFormat)
        logString = logString+'\n\t\tLocal: '+str(lFormat)+'\n\t\tMaster: '+str(mFormat)

        logString = logString+'\n\tImprint (260):\n\t\tLocal :'+str(local260a)+'\n\t\tMaster: '+str(master260a)
        logString = logString+'\n\tSeries(440): \n\t\tLocal: \n\t\t'+local440st+'\n\t\tMaster: \n\t\t'+master440st
        logString = logString+'\n\tSeries(490):\n\t\tLocal: \n\t\t'+local490st+'\n\t\tMaster: \n\t\t'+master490st
        logString = logString+'\n\tSeries(830):\n\t\tLocal: \n\t\t'+local830st+'\n\t\tMaster: \n\t\t'+master830st
        logString = logString+'\n\tLocal 440 tag found in 830 Master:\n\t\t'+compResult

        logResult(str(keyCounter), logString)

        # try:
        #     print('List#: '+str(keyCounter) +
        #           '\nKey: '+str(key)+'\n\tLocal Sys#: '+str(lSysNumber) +
        #           '\n\tOCLC Numbers:\n\t\tLocal:'+str(oclcNumberL)+'\n\t\tMaster'+str(oclcNumberM)+'\n' +
        #           '\n\tImprint (260):\n\t\tLocal:'+str(local260a)+'\n\t\tMaster'+str(master260a)+'\n'
        #           )
        # except UnicodeEncodeError:
        #     print('List#: '+str(keyCounter)+' had error in writing')

        stop = False
        # stop = checkForBreak()
        if stop:
            return

        keyCounter += 1

    now = time.strftime('%Y-%m-%d %H:%M:%S')
    now = 'finished at: '+str(now)
    logStartEnd(now)
    print(now)

    print('... DONE!')

# runComparison()

def returnString(d, dictKey):
    """returns a list of strings based on a provided list with dictionaries and key of dictionary"""

    strList = []
    for sub in d:
        strResult = ''
        for di in sub[dictKey]['subfields']:
            for key in di:
                if key != '5':
                    strResult = strResult + str(key)+': '+str(di[key])+' | '
        strList.append((strResult))

    return strList

def writeLocalCheckResults(resultList, lSysNumber):

    y = []
    x = []
    for a in resultList:
        if len(a) > 0:
            x.append(a)

    y.append(x)

    localResultCheck = 'localResultLog.csv'

    # print(x)

    with open(localResultCheck, 'a', newline='') as out:
        a = csv.writer(out, delimiter=',', quoting=csv.QUOTE_ALL)
        try:
            a.writerows(y)
        except UnicodeEncodeError:
            print("error Encoding: system number ", lSysNumber)
        except UnicodeDecodeError:
            print("error Decoding: system number ", lSysNumber)

def returnlocal440List(local440):
    """Only works for 440... returns the subfields in a list"""

    local440L = []
    for a in local440:
        local440L.append(a['440']['subfields'])

    return local440L

def compare440to490to830(lSysNumber, oclcNumberL, local440, local490, local830):

    stop = False

    l440 = returnString(local440, '440')
    l440a = stringValStrip(l440)

    l490 = returnString(local490, '490')
    l490a = stringValStrip(l490)

    l830 = returnString(local830, '830')
    l830a = stringValStrip(l830)

    resultList = []
    # for x in l440:
    #     print('checking ', x)
    counter440 = 0
    for a in l440a:
        # print('checking ', a)
        seriesFound = False
        tempList = []
        for b in l490a:
            # print(a, b, a == b)
            if a == b:
                seriesFound = True
                # print('seriesFound!')
            if seriesFound == False:
                for b in l830a:
                    # print(a, b, a == b)
                    if a == b:
                        seriesFound = True
                        # print('seriesFound!')
            # print('seriesFound: ', a, seriesFound)
            # print(tempList)
        # print(seriesFound)
        # input('waiting...')
        if seriesFound == False:
            tempList.append(lSysNumber)
            tempList.append(oclcNumberL)
            tempList.append(local440[counter440])
            # tempList.append(seriesFound)
        # print(tempList)
        resultList.append(tempList)
        counter440 =+ 1

        # stop = checkForBreak()
        if stop:
            return

    return resultList


def localCheck():
    now = time.strftime('%Y-%m-%d %H:%M:%S')
    now = 'starting at: '+str(now)
    # logStartEnd(now)
    print(now)


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

        local440 = getTags(lDict[key], '440')
        local440st = stringFormDict(local440)

        if local440st is None:
            continue

        local490 = getTags(lDict[key], '490')
        local830 = getTags(lDict[key], '830')

        comparisonResults = []
        comparisonResults = compare440to490to830(lSysNumber, oclcNumberL, local440, local490, local830)
        for a in comparisonResults:
            if len(a) > 0:
                writeLocalCheckResults(a, lSysNumber)


        stop = False
        # stop = checkForBreak()
        if stop:
            return

        keyCounter += 1

    now = time.strftime('%Y-%m-%d %H:%M:%S')
    now = 'finishing at: '+str(now)
    # logStartEnd(now)
    print(now)

def betterComparison(lista, listb, listc, listd, liste):

    unfoundSeriesStringList = []

    for series in lista:
        if series in listb:
            print("found")
            break
        if series in listc:
            print("found")
            break
        if series in listd:
            print("found")
            break
        if series in liste:
            print("found")
            break

        unfoundSeriesStringList.append(series)

    return unfoundSeriesStringList

def betterCheck():

    now = time.strftime('%Y-%m-%d %H:%M:%S')
    now = 'starting at: '+str(now)
    logStartEnd(now)
    print(now)


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

        # Return Formats
        lFormat = returnFormat(lDict[key])
        mFormat = returnFormat(mDict[key])
        matchFormat = False
        if lFormat == mFormat:
            if lFormat.upper() == "UNKNOWN":
                lFormat = "Unknown"
            else:
                matchFormat = True

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

        #Begin logging protocol
        logString = 'List#: '+str(keyCounter)+'\nKey: '+str(key)+'\n\tLocal Sys#: '+str(lSysNumber)

        # add oclc numbers
        logString = logString+'\n\tOCLC Numbers:\n\t\tLocal: '+str(oclcNumberL)+'\n\t\tMaster: '+str(oclcNumberM)

        # add formats
        logString = logString+'\n\tFormats (008 23): Formats Match?: '+str(matchFormat)
        logString = logString+'\n\t\tLocal: '+str(lFormat)+'\n\t\tMaster: '+str(mFormat)

        logString = logString+'\n\tImprint (260):\n\t\tLocal :'+str(local260a)+'\n\t\tMaster: '+str(master260a)
        logString = logString+'\n\tSeries(440): \n\t\tLocal: \n\t\t'+local440st+'\n\t\tMaster: \n\t\t'+master440st
        logString = logString+'\n\tSeries(490):\n\t\tLocal: \n\t\t'+local490st+'\n\t\tMaster: \n\t\t'+master490st
        logString = logString+'\n\tSeries(830):\n\t\tLocal: \n\t\t'+local830st+'\n\t\tMaster: \n\t\t'+master830st


        ######THIS BIT IS THE SHINY NEW COMPARISON STRUCTURE!

        #get string versions of the lists in each field
        l440 = returnString(local440, '440')
        l440 = stringValStrip(l440)

        l490 = returnString(local490, '490')
        l490 = stringValStrip(l490)

        l830 = returnString(local830, '830')
        l830 = stringValStrip(l830)

        m490 = returnString(master490, '490')
        m490 = stringValStrip(m490)

        m830 = returnString(master830, '830')
        m830 = stringValStrip(m830)

        #for troubleshooting, log the comparision strings
        logString = logString+'\n\tComparison Strings:'
        logString = logString+'\n\t\tlocal440: '+str(l440)
        logString = logString+'\n\t\tlocal490: '+str(l490)
        logString = logString+'\n\t\tlocal830: '+str(l830)
        logString = logString+'\n\t\tmaster490: '+str(m490)
        logString = logString+'\n\t\tmaster830: '+str(m830)

        #Do the actual comparison!

        compResult = betterComparison(l440, l490, l830, m490, m830)
        compResultString = ''
        if len(compResult) == 0:
            compResultString = 'None'
        else:
            for result in compResult:
                compResultString = compResultString+result+'\n'

        logString = logString+'\n\tComparison Strings Not Found:'+'\n\t\t'+compResultString


        #######################################################

        # logString = logString+'\n\tLocal 440 tag found in 830 Master:\n\t\t'+compResult

        logResult(str(keyCounter), logString)


        stop = False
        stop = checkForBreak()
        if stop:
            return

        keyCounter += 1

    now = time.strftime('%Y-%m-%d %H:%M:%S')
    now = 'finished at: '+str(now)
    logStartEnd(now)
    print(now)

    print('... DONE!')