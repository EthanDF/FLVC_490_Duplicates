from pymarc import *
import csv


def getBib(marc):
    try:
        bib = marc['001'].value()
    except AttributeError:
        bib = None
    return bib

def writeToOCLCNumList(bib, oclcNumber, format):
    """writes to a log file the BIB and OCLC number of a record found to be an OCLC number"""
    oclcFile = 'oclc_numbers.csv'

    import time
    now = time.strftime('%Y-%m-%d %H:%M:%S')
    data = [[now, str(bib), str(oclcNumber), str(format)]]
    # print(data)

    with open(oclcFile, 'a', newline='') as out:
        a = csv.writer(out, delimiter=',', quoting=csv.QUOTE_ALL)
        a.writerows(data)

def writeLog(logString):
    logFile = 'logFile.txt'

    with open(logFile, 'a') as log:
        log.write('\n'+logString+'\n')

def getControlNumber(record):
    oclc = ''

    o = record.get_fields('035')

#   check that all values in list of 035 values are OCoLC

    oclcYes = 1

    if len(o) == 0:
        oclcYes = 0
    else:
        for ovalue in o:
            if 'OCoLC' in ovalue.value():
                pass
            else:
                oclcYes = 0

    if oclcYes == 1:
        bib = getBib(record)
        format = returnFormat(record)
        oclcNumber = record['035']['a']
        writeToOCLCNumList(bib, oclcNumber, format)

#   the original part of this call - just checks for OCLC Number and does the print out
    for o in record.get_fields('035'):
        if 'OCoLC' in o.value():
            oclc = o.value()
        else:
            print('Non OCLC Number', o.value())

    return oclc


def returnFormat(record):
    formatCode = record['008'].value()[23:24]

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


def move440to490(record):
    """take the 440 value and match it to existing 490 values.
    match a 440 to 490, append subfield 5s that aren't there already
    if no 490 match is found, create a 490 from the 440 with the same
    subfield 5 values"""

    list440 = has440(record)
    list490 = has490(record)

    for a in list440:
        temp440 = a['a']
        for b in list490:
            if temp440 == b['a']:
                # print('\t\tmatch!', b['a'])
                # print("\t\tcheck $5 values if they don't already exist", a.get_subfields('5'), 'to ', b.get_subfields('5'))

#               what subfield 5 values of b (the current 440) already exist for a (the current 490)?
                tempListOfSubfield5s = []

                # print(b)
                for b5 in a.get_subfields('5'):
                    # print(b5)
                    # print(b.get_subfields('5'))
                    if b5 not in b.get_subfields('5'):
                        # print('\t\tappend ', b5)
                        pass
                    else:
                        # print(b5, '\t\tis already a subfield 5 value in ', b.get_subfields('5'))
                        pass


def has440(record):
    List440 = []
    for o in record.get_fields('440'):
        List440.append(o)

    return List440


def remediate490(list490):
    """This is where the remediation should occur for the 490 fields"""

    indicator1True = 0
    indicator1False = 0

    if o.indicator1 == '1':
        indicator1True = 1

    if o.indicator1 == '0':
        indicator1False = 1

    indicatorList = [indicator1True, indicator1False]

    return indicatorList

    pass
    # for i in list490:
    # print(i)

    # input('wait for approval')


def has490(record):
    List490 = []

    for o in record.get_fields('490'):
        List490.append(o)

    return List490

def marc490():
    marcFile = '10k.mrc'

    recordCounter = 0
    with open(marcFile, 'rb') as fh:
        reader = MARCReader(fh, to_unicode=True, force_utf8=True)

        for record in reader:
            recordCounter += 1
            record.force_utf8 = True

            marc = record.as_marc()
            marc = marc.decode('utf-8')
            # return marc

            bib = getBib(record)
            if bib is None:
                bib = "None"
            oclc = getControlNumber(record).strip()
            if oclc is None:
                oclc = 'None'

            # There is a suggestion that electronic records should be excluded from the results of this script

            format = returnFormat(record)
            if format is None:
                format = 'None'

            values440 = has440(record)
            values490 = has490(record)
            if record['STA'] == None:
                staVal = 'None'
            else:
                staVal = record['STA'].value().strip()

            logString = ''

            logString = '\nrecord#: '+str(recordCounter)+'\nBib is: '+bib+'\nOCLC#: '+oclc.strip()+'\nFormat: ' +\
                        format.strip()+'\nStatus: '+staVal+'\n440 values:'

            # print(logString)

            # print('\nrecord#:', str(recordCounter))
            # print('Bib is: ', bib, '\nOCLC#: ', oclc.strip(), '\nFormat: ', format.strip(), '\nStatus: ', staVal,
                  # '\n440 values:')

            if values440 is None:
                pass
            else:
                for a in values440:
                    try:
                        print('\t', a)
                        logString = logString+'\n\t'+str(a)
                    except (UnicodeEncodeError, UnicodeDecodeError):

                        print('\t', "****can't print due to encoding issue****")
                        logString = logString+'\n\t'+"****can't print due to encoding issue****"

                    move440to490(record)
            # print(logString)

            # print('490 values:')
            logString = logString+'\n490 Values:'

            # print(logString)

            if values490 is None:
                pass
            else:
                for b in values490:
                    try:
                        print('\t', b)
                        logString = logString+'\n\t '+str(b)
                    except UnicodeEncodeError:
                        print('\t', "****can't print due to encoding issue****")
                        logString = logString+"\n\t ****can't print due to encoding issue****"

            # return record
            print(logString)

            # print ('830 values:')
            logString = logString+'\n830 values: '

            # print(logString)
            for a in record.get_fields('830'):
                try:
                    print('\t', a)
                    logString = logString+'\n\t'+str(a)
                except (UnicodeEncodeError, UnicodeDecodeError):
                    print('\t', "****can't print due to encoding issue****")
                    logString = logString+'\n\t'+"****can't print due to encoding issue****"

            writeLog(logString)
            # print(logString)
            # goOn = input('continue?\n')
            #
            # if goOn == 'n':
            #     return record

marc490()