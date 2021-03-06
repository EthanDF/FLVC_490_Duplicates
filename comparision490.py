from pymarc import *
import json
import time
import csv
import codecs
import unicodedata

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
            rec.force_utf8 = True
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
                    # if tempKey == 36126777:

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
    arts = ['the', 'a', 'an', 'el', 'los', 'la', 'las', 'un', 'unos', 'una', 'unas', 'le', 'la', 'l�', 'les', 'un',
            'une', 'des', 'no.', 'vol', 'no', 'vol.', 'v.', 'v', '[no.', 'a:']

    punct = [';', ',', '.', '[', ']', '<', '>', '|', '(', ')', '-', '{', '}', ':', '?', '�', '!', "'", '"', "/", '\\',
             '1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
             '?']

    unicodeChar = ['\u0301', '?', '\u0306']

    afterListItem = []
    for listItem in listString:
        tempafterListItem = []
        #replace articles from list arts, split each word into the list and see if that word is in the arts list - if so remove it, then recomplile into a string.
        llist = listItem.split(' ')
        # print(llist)
        for w in llist:
            if w == 'v:':
                break
            if w.upper() not in [x.upper() for x in arts] and w not in punct:

                # for char in unicodeChar:
                #     w = unicodedata.normalize('NFD', w)

                # for char in unicodeChar:
                #     if char in w:
                #         w = w[:w.find(char)-1]+w[w.find(char)+1:]

                # w = w.encode('ascii', 'replace')
                # w = w.decode('utf-8')
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

        # strip out any punctuation

        stTempAfterListItem2 = ''
        for letter in stTempAfterListItem:
            if letter not in punct:
                stTempAfterListItem2 = stTempAfterListItem2+letter


        # remove cases where pronouns appear in the first 4 characters
        startingProunouns = ['SHE ', 'HIS ', 'HER ', 'HIM ']

        # print(stTempAfterListItem2)

        if stTempAfterListItem2[0:4].upper() in startingProunouns:
            # print("found!")
            stTempAfterListItem2 = stTempAfterListItem2[4:]
        else:
            stTempAfterListItem2 = stTempAfterListItem2

        stTempAfterListItem = stTempAfterListItem2.strip()

        afterListItem.append(stTempAfterListItem)

    # print(afterListItem)
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

def returnOCLC(sentdict):

    result035 = ''
    # print(sentdict)

    for v in sentdict['fields']:
        # input('')
        # v
        for k in v:
            # print('in v')
            # k
            if k == '035':
                # print('035 found!')
                # k
                useVals  = v['035']['subfields']
                for subDict in useVals:
                    for tag in subDict:
                        # print(tag)
                        # print(tag == 'a')
                        # print(subDict[tag][0:6])
                        if tag == 'a' and subDict[tag][0:7] == '(OCoLC)':
                            # print(subDict[tag])
                            result035 = subDict[tag]
                            return result035

def logStartEnd(now):
    testinglogFile = 'testinglogFile.txt'
    with open(testinglogFile, 'a') as log:
        try:
            log.write(now)
        except UnicodeEncodeError:
            log.write('\n'+'failed to write record key: '+str(recordKey)+'\n')

def logResult(recordKey, logString):

    testinglogFile = 'testinglogFile.txt'
    with codecs.open(testinglogFile, 'a', encoding='utf-8') as log:
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

def returnString(d, dictKey):
    """returns a list of strings based on a provided list with dictionaries and key of dictionary"""

    strList = []
    for sub in d:
        strResult = ''
        for di in sub[dictKey]['subfields']:
            for key in di:
                if key in('a', 'p'):
                    strResult = strResult + str(key)+': '+str(di[key])+' | '
        strList.append((unicodedata.normalize('NFD', strResult)))

    return strList

def writeLocalCheckResults(resultList, lSysNumber):

    y = []
    x = []
    for a in resultList:
        if a is None:
            x.append('None')
            continue
        if len(a) > 0:
            x.append(a)

    y.append(x)

    localResultCheck = 'bibsAndSeriesCannotOverlay.csv'

    # print(x)

    with codecs.open(localResultCheck, 'a', encoding='utf-8') as out:
        a = csv.writer(out, delimiter=',', quoting=csv.QUOTE_ALL)
        try:
            a.writerows(y)
        except UnicodeEncodeError:
            print("error Encoding: system number ", lSysNumber)
        except UnicodeDecodeError:
            print("error Decoding: system number ", lSysNumber)

def writeAuthorityReviewSet(resultList, lSysNumber):

    if lSysNumber is None:
        lSysNumber = 'None'
    y = []
    x = []
    for a in resultList:
        if a is None:
            x.append("None")
            continue
        if len(a) > 0:
            x.append(a)

    y.append(x)

    localResultCheck = 'AuthorityReviewSet.csv'

    # print(x)

    with codecs.open(localResultCheck, 'a', encoding='utf-8') as out:
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

def betterComparison(lista, listb, listc, listd, liste):

    unfoundSeriesStringList = []
    badEndingValues = ['V']
    beginningWords = ['he ', 'her', 'his', 'she']

    listaa = []
    listbb = []
    listcc = []
    listdd = []
    listee = []

    for a in lista:
        if len(a) > 0 and a.upper()[-1] in badEndingValues:
            a = a[0:len(a)-1].strip()
        listaa.append(a.upper())
    for a in listb:
        if len(a) > 0 and a.upper()[-1] in badEndingValues:
            a = a[0:len(a)-1].strip()
        listbb.append(a.upper())
    for a in listc:
        if len(a) > 0 and a.upper()[-1] in badEndingValues:
            a = a[0:len(a)-1].strip()
        listcc.append(a.upper())
    for a in listd:
        if len(a) > 0 and a.upper()[-1] in badEndingValues:
            a = a[0:len(a)-1].strip()
        listdd.append(a.upper())
    for a in liste:
        if len(a) > 0 and a.upper()[-1] in badEndingValues:
            a = a[0:len(a)-1].strip()
        listee.append(a.upper())


    for series in listaa:
        if series in listbb:
            # print("found")
            continue
        if series in listcc:
            # print("found")
            continue
        if series in listdd:
            # print("found")
            continue
        if series in listee:
            # print("found")
            continue

        unfoundSeriesStringList.append(series)

    return unfoundSeriesStringList

def checkSubFields(tagDictionary, key):
    """Checks to see if the subfields in the local 440 are in the list
    that would disqualify them from being local series
    tagDictionary should be local440 """

    localSeriesList = ['n', 'p', 'v', 'w', 'x', '0', '6', '8', '5']

    subfieldContinue = True
    subfieldList = []
    for dict in tagDictionary:
        for subDict in dict[key]['subfields']:
            for k in subDict:
                subfieldList.append(k)

    for sf in subfieldList:
        if sf in localSeriesList:
            subfieldContinue = False
            return subfieldContinue

    return subfieldContinue

def controlled(m490):
    """check the local 490 for cases where the indicator = 1 and there is an 830
       check the master 490 for and indicator = 0 and no 830
       return true or false for meeting this condition"""

    controlledHeading = False
    # ind1L490 = True
    ind1M490 = False
    # hasL830 = False
    hasNo490 = False

    # for ind in l490:
    #     ind1L490Value = ind['490']['ind1']
    #     # print(ind1L490Value)
    #     if ind1L490Value == '1':
    #         ind1L490 = True

    # if len(l830) > 0:
    #     hasL830 = True

    for ind in m490:
        ind1M490Value = ind['490']['ind1']
        # print(ind1M490Value)
        if ind1M490Value == '0':
            ind1M490 = True

    if len(m490) == 0:
        hasNo490 = True

    if(ind1M490 or hasNo490):
        controlledHeading = True


    # print(ind1L490, ind1M490, hasL830, hasNoM830, controlledHeading)

    return controlledHeading

def referenceKeys(mDict):

    referenceDict = {}
    m035 = 0
    ref = 0

    for record in mDict:
        # input('continue...')
        fields = mDict[record]['fields']
        for field in fields:
            # print(field)
            for key in field:
                # print(key)
                if key == '001':

                    m035 = field[key]
                    # print(sf)
                    m035 = m035.replace('ocm', '')
                    m035 = m035.replace('ocn', '')
                    # print(m035)
                        # input('key = 035!: ',m035)
                if key == '019':
                    # input('found 019')
                    sf = field[key]['subfields']
                    for refVal in sf:
                        # print('019 is: ', refVal)
                        ref = refVal['a']
                        # print(ref)
                        referenceDict[int(ref)] = int(m035)

                    # for s in sf:
                    #     m019List = s[]


            # try:
            #     m035List = field['035']['subfields']
            #     input(m035List)
            #     for sysNum in m035List:
            #         m035 = sysNum['a']
            # except KeyError:
            #     print(field['001'])
            #     break
            #
            # try:
            #     m019List = field['019']['subfields']
            #     for subfield in m019List:
            #         m019 = subfield['a']
            #         # print(m019)
            #         referenceDict[m019] = m035
            # except KeyError:
            #     pass

    return referenceDict

def buildADict(lKeys, mKeys, rDict):

    aDict = {}

    for key in lKeys:
        # print(key)

        if key in mKeys:
            aDict[key] = key

        else:
            # print('not found')
            try:
                aDict[key] = rDict[key]
            except KeyError:
                print(key, "not found, will be skipped")

            stop = False
            # stop = checkForBreak()
            if stop:
                return

    return aDict

def writeCompResultString(compResult):
    compResultString = ''

    if len(compResult) == 0:
        compResultString = 'None'
    else:
        for result in compResult:
            compResultString = 'Not Found!\n\t\t'+compResultString+result+'\n'

    return compResultString

def writeBibsForOverlay(localSystemNumber, localOCLCNumber, overlay):
    # overlay = 1 implies yes
    bibFile = 'bibsForOverlay.csv'


    # print(x)
    x = []
    y = []
    x.append(localSystemNumber)
    x.append(localOCLCNumber)
    x.append(overlay)
    y.append(x)

    with codecs.open(bibFile, 'a', encoding='utf-8') as out:
        a = csv.writer(out, delimiter=',', quoting=csv.QUOTE_ALL)
        try:
            if len(y) > 0:
                a.writerows(y)
        except UnicodeEncodeError:
            print("error Encoding: system number ", localSystemNumber)
        except UnicodeDecodeError:
            print("error Decoding: system number ", localSystemNumber)

def spitOutMismatchedOCLCNumbers(localSystemNumber, localOCLCNumber, masterOCLCNumber):
    # overlay = 1 implies yes
    logFile = 'mismatchedOCLCNumbers.csv'

    # print(x)
    x = []
    y = []
    x.append(localSystemNumber)
    x.append(localOCLCNumber)
    x.append(masterOCLCNumber)
    y.append(x)

    with open(logFile, 'a', newline='') as out:
            a = csv.writer(out, delimiter=',', quoting=csv.QUOTE_ALL)
            a.writerows(y)

def betterCheck():

    now = time.strftime('%Y-%m-%d %H:%M:%S')
    now = 'starting at: '+str(now)
    logStartEnd(now)
    print(now)


# Create dictionaries from the local and master marc files
    print('\nbuilding dictionaries...')
    lDict = marc490('10k.mrc')
    mDict = marc490('490OCLC.mrc')
    rDict = referenceKeys(mDict)
    print('... DONE!')

# Gets list of keys from the 2 dictionaries, and a third list of common keys
    print('\nbuilding lists...')
    lKeys = returnKeyList(lDict)
    mKeys = returnKeyList(mDict)
    # aKeys = compareKeyList(lKeys, mKeys)
    aDict = buildADict(lKeys, mKeys, rDict)
    print('... DONE!')

# return, for comparison the two OCLC numbers in the records
    print('\ncomparing results and writing to log')
    keyCounter = 0
    for key in aDict:

        # if key == 747798947:
        #     input('found 747798947')
        stop = False
        # stop = checkForBreak()
        if stop:
            return

        lSysNumber = getTagValues(lDict[key], '001', None)

        oclcNumberL = returnOCLC(lDict[key])
        oclcNumberM = returnOCLC(mDict[aDict[key]])

        # Return Formats
        lFormat = returnFormat(lDict[key])
        mFormat = returnFormat(mDict[aDict[key]])
        matchFormat = False
        if lFormat == mFormat:
            if lFormat.upper() == "UNKNOWN":
                lFormat = "Unknown"
            else:
                matchFormat = True

        local245a = getTagValues(lDict[key], '245', 'a')
        master245a = getTagValues(mDict[aDict[key]], '245', 'a')
        local440 = getTags(lDict[key], '440')
        local440st = stringFormDict(local440)
        master440 = getTags(mDict[aDict[key]], '440')
        master440st = stringFormDict(master440)

        local490 = getTags(lDict[key], '490')
        local490st = stringFormDict(local490)
        master490 = getTags(mDict[aDict[key]], '490')
        master490st = stringFormDict(master490)

        local830 = getTags(lDict[key], '830')
        local830st = stringFormDict(local830)
        master830 = getTags(mDict[aDict[key]], '830')
        master830st = stringFormDict(master830)

        #Begin logging protocol
        logString = 'List#: '+str(keyCounter)+'\nKey: '+str(key)+'\n\tLocal Sys#: '+str(lSysNumber)

        # add oclc numbers
        logString = logString+'\n\tOCLC Numbers:\n\t\tLocal: '+str(oclcNumberL)+'\n\t\tMaster: '+str(oclcNumberM)

        if int(oclcNumberL.replace("(OCoLC)", "")) != int(oclcNumberM.replace("(OCoLC)", "")):
            logString = logString+'\n\t\tOCLC Mismatch'
            spitOutMismatchedOCLCNumbers(lSysNumber, oclcNumberL, oclcNumberM)

        # add formats
        logString = logString+'\n\tFormats (008 23): Formats Match?: '+str(matchFormat)
        logString = logString+'\n\t\tLocal: '+str(lFormat)+'\n\t\tMaster: '+str(mFormat)

        logString = logString+'\n\tTitle (245):\n\t\tLocal :'+str(local245a)+'\n\t\tMaster: '+str(master245a)
        logString = logString+'\n\tSeries(440): \n\t\tLocal: \n\t\t'+local440st+'\n\t\tMaster: \n\t\t'+master440st
        logString = logString+'\n\tSeries(490):\n\t\tLocal: \n\t\t'+local490st+'\n\t\tMaster: \n\t\t'+master490st
        logString = logString+'\n\tSeries(830):\n\t\tLocal: \n\t\t'+local830st+'\n\t\tMaster: \n\t\t'+master830st

        ###Put in the test 1 check for subfield here: reference checkSubFields

        # localSeriesCheck = controlled(local490, local830, master490, master830)
        localSeriesCheck = controlled(master490)

        if localSeriesCheck:
            logString = logString+'\n\tGoes into the Authority Review Set:'
            logResult(str(keyCounter), logString)
            keyCounter += 1
            sendForAuthReview = [lSysNumber, oclcNumberL, local490, local830, master490, master830]
            writeAuthorityReviewSet(sendForAuthReview, lSysNumber)
            writeBibsForOverlay(lSysNumber, oclcNumberL, '0')
            continue

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

        wasteList = ['-1']

        #Compare Local440
        compResult = betterComparison(l440, m490, m830, wasteList, wasteList)
        compResultString = writeCompResultString(compResult)
        ###LOG ACTIONABLE Results Log
        if len(compResult) > 0:
            sendForLocalCheckResults = [lSysNumber, oclcNumberL, '440', local440]
            writeLocalCheckResults(sendForLocalCheckResults, lSysNumber)
            logString = logString+'\n\tComparison Strings Not Found (440):'+'\n\t\t'+compResultString
            writeBibsForOverlay(lSysNumber, oclcNumberL, '0')
            logResult(str(keyCounter), logString)
            keyCounter += 1
            continue

        #Compare Local490
        compResult = betterComparison(l490, m490, m830, wasteList, wasteList)
        compResultString = writeCompResultString(compResult)
        ###LOG ACTIONABLE Results Log
        if len(compResult) > 0:
            sendForLocalCheckResults = [lSysNumber, oclcNumberL, '490', local490]
            writeLocalCheckResults(sendForLocalCheckResults, lSysNumber)
            logString = logString+'\n\tComparison Strings Not Found (490):'+'\n\t\t'+compResultString
            writeBibsForOverlay(lSysNumber, oclcNumberL, '0')
            logResult(str(keyCounter), logString)
            keyCounter += 1
            continue

        #Compare Local830
        compResult = betterComparison(l830, m830, wasteList, wasteList, wasteList)
        compResultString = writeCompResultString(compResult)
        ###LOG ACTIONABLE Results Log
        if len(compResult) > 0:
            sendForLocalCheckResults = [lSysNumber, oclcNumberL, '830', local830]
            writeLocalCheckResults(sendForLocalCheckResults, lSysNumber)
            logString = logString+'\n\tComparison Strings Not Found (830):'+'\n\t\t'+compResultString
            writeBibsForOverlay(lSysNumber, oclcNumberL, '0')
            logResult(str(keyCounter), logString)
            keyCounter += 1
            continue

        stop = False
        # stop = checkForBreak()
        if stop:
            return

        #######################################################

        # logString = logString+'\n\tLocal 440 tag found in 830 Master:\n\t\t'+compResult

        #If the loop is still here, the record is okay to overlay
        writeBibsForOverlay(lSysNumber, oclcNumberL, '1')
        logResult(str(keyCounter), logString)

        keyCounter += 1

    now = time.strftime('%Y-%m-%d %H:%M:%S')
    now = 'finished at: '+str(now)
    logStartEnd(now)
    print(now)

    print('... DONE!')