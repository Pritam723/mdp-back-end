import os
from django.core.files import File
import re
from datetime import datetime,timedelta


###################################################  Global Variables #######################################################################
checkTimeStamp = ['00','04','08','12','16','20']
statusCodes =  ['Uploaded' , 'Extracted' , 'Merged' , 'DateFiltered','Verified', 'MWHCreated', 'FictCreated' , 'FinalOutputCreated' ]
#############################################################################################################################################


###################################################  Global Functions #######################################################################

def extraCharHandler(value) :
    # Handles '*' , 'a' , 'z' , 'r' extra characters.
    while '*' in value:   
        value.remove('*')
    while 'z' in value:   
        value.remove('z')
    while 'a' in value:   
        value.remove('a')
    while 'r' in value:   
        value.remove('r')
    return value
    
def initialCharHandler(value) :
    # Handles 'aa' , 'rr' initials.
    if(value[0] == 'a' and value[1] == 'a') :
        value = value[2:]
        return value
    elif(value[0] == 'r' and value[1] == 'r') :
        value = value[2:]
        return value
    else :
        return value
    
def isFloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def isTwoDigitFloat(value):
    value = initialCharHandler(value)
    twoDigitFloatPattern = re.compile(r'^[0-9]{2}$')
    result = re.match(twoDigitFloatPattern, value)
    if((result is not None) and (isFloat(value))) :
        return True
    else :
        return False
    
def isSixDigitFloat(value):
    value = initialCharHandler(value)
    sixDigitFloatPattern = re.compile(r'^[+-][0-9]{2}\.[0-9]{2}$')
    result = re.match(sixDigitFloatPattern, value)
    if((result is not None) and (isFloat(value))) :
        return True
    else :
        return False

def isSevenDigitFloat(value):
    value = initialCharHandler(value)
    sevenDigitFloatPattern = re.compile(r'^[0-9]{5}\.[0-9]$')
    result = re.match(sevenDigitFloatPattern, value)
    if((result is not None) and (isFloat(value))) :
        return True
    else :
        return False
    
def isSevenEightDigitFloat(value):
    value = initialCharHandler(value)
    sevenEightDigitFloatPattern = re.compile(r'^[+-]?[0-9]{4}\.[0-9]{2}$')
    result = re.match(sevenEightDigitFloatPattern, value)
    if((result is not None) and (isFloat(value))) :
        return True
    else :
        return False
    
def isDate(value) :
    datePattern = re.compile(r'^[0-9]{2}-[0-9]{2}-[0-9]{2}$')
    result = re.match(datePattern, value)
    if(result is None) :
        return False                                             
    try:
        datetime.strptime(value, "%d-%m-%y")
        return True
    except ValueError:
        return False


def isTime(value) :
    import time
    timePattern = re.compile(r'^[0-2][0-9][0-5][0-9]$')
    result = re.match(timePattern, value)
    if(result is None) :
        return False                                             
    try:
        time.strptime(value, '%H%M')
        return True
    except ValueError:
        return False
                                          
def isMeterNumberPattern(value) :
    meterNumberPattern = re.compile(r'^[A-Z]{2}-[0-9]{4}-[A-Z]$')
    result = re.match(meterNumberPattern, value)
    if result:
        return True
    else:
        return False
    
def isMeterIdPattern(value) :
    meterIdPattern = re.compile(r'^[A-Z]{2}-[0-9]{2}$')
    result = re.match(meterIdPattern, value)
    if result:
        return True
    else:
        return False

def isMeterNameUnique(nameList) :
    
    return(len(set(nameList)) == 1)

def isMeterDateConsecutive(dateList,startObj,endObj) :
    
    if(dateList[0] != startObj or dateList[-1] != endObj) :
        return False

    for day in range((endObj-startObj).days+1) :
        if(dateList[day] != startObj+timedelta(days=day)) :
            return False

    return True

def getDfInfo(_weekList,_meterHeaderList) :
    informationDict = {}
    meterHeaderIndex = 0
    for weekHeaderIndex in range(len(_weekList)-1):
        informationDict[_weekList[weekHeaderIndex]] = []  # Makes a dictionary index with weekHeaderIndex
        while meterHeaderIndex < len(_meterHeaderList) and _weekList[weekHeaderIndex] < _meterHeaderList[meterHeaderIndex] < _weekList[weekHeaderIndex + 1]:
            informationDict[_weekList[weekHeaderIndex]].append(_meterHeaderList[meterHeaderIndex])
            meterHeaderIndex+=1
        informationDict[_weekList[weekHeaderIndex]].append(_weekList[weekHeaderIndex+1])
    return(informationDict)


#############################################################################################################################################


###################################################  Specific Functions #######################################################################

# ************************************************ Helps Extract *******************************************************
# No function yet

# ************************************************ Helps DateFilter *******************************************************

def meterHeaderCheckDate(rowList) :
    
    if(len(rowList) != 5) :

        return {"message" : "Structural error.(Can be Missing data/ extra space/ non-uniformity). Line number : ", "status" : False}

    if(not isDate(rowList[4])) :

        return {"message" : "Date format mismatch : "+ str(rowList[4]) +". Line number : ", "status" : False}
    
    return {"message" : "All checked." , "status" : True}

def weekHeaderCheckDate(rowList) :
    
    if(len(rowList) != 11) :
        return {"message" : "Structural error.(Can be Missing data/ extra space/ non-uniformity). Line number : ", "status" : False}

    if(not isTime(rowList[2])) :
        return {"message" : "Timestamp format mismatch : "+ str(rowList[2]) +". Line number : ", "status" : False}
    if(not isTime(rowList[7])) :
        return {"message" : "Timestamp format mismatch : "+ str(rowList[7]) +". Line number : ", "status" : False}
    if(not isDate(rowList[5])) :
        return {"message" : "Date format mismatch : "+ str(rowList[5]) +". Line number : ", "status" : False}
    if(not isDate(rowList[10])) :
        return {"message" : "Date format mismatch : "+ str(rowList[10]) +". Line number : ", "status" : False}
    
     # If I reach here, I am pretty sure that both the dates are in correct format.
    if(datetime.strptime(rowList[10], "%d-%m-%y") < datetime.strptime(rowList[5], "%d-%m-%y")) :  
        return {"message" : "Date format mismatch. End date smaller than start date. Line number : ", "status" : False}
    
    return {"message" : "All checked." , "status" : True}

# ************************************************ Helps Validate *******************************************************
def mainMeterDataCheck(rowList) :

    #  len(rowList) must be odd, if timestamp not = '20'

    if(rowList[0] == '20') :
        if(not (len(rowList) >= 33)) :
            return {"message" : "Structural error.(Can be Missing data/ extra space/ non-uniformity). Line number : " , "status" : False }
        
        for rowListIndex in range(1,len(rowList)-1) :
            if(rowListIndex % 2 == 1) :
                if(not isTwoDigitFloat(rowList[rowListIndex])) :
                    return {"message" : "Format error in frequency data : " + str(rowList[rowListIndex]) +". Line number : " , "status" : False }
            else :
                if(not isSixDigitFloat(rowList[rowListIndex])) :
                    return {"message" : "Format error in active energy data : "+ str(rowList[rowListIndex]) +". Line number : " , "status" : False }
                
        return {"message" : "All checked." , "status" : True}

    else :
        if(not (len(rowList) == 33)) :
            return {"message" : "Structural error.(Can be Missing data/ extra space/ non-uniformity). Line number : ", "status" : False}
        for rowListIndex in range(1,len(rowList)) :
            if(rowListIndex % 2 == 1) :
                if(not isTwoDigitFloat(rowList[rowListIndex])) :
                    return {"message" : "Format error in frequency data : " + str(rowList[rowListIndex]) +". Line number : " , "status" : False }
            else :
                if(not isSixDigitFloat(rowList[rowListIndex])) :
                    return {"message" : "Format error in active energy data : " + str(rowList[rowListIndex]) +". Line number : " , "status" : False }
        
        return {"message" : "All checked." , "status" : True}

def meterHeaderCheck(rowList) :
    
    if(len(rowList) != 5) :

        return {"message" : "Structural error.(Can be Missing data/ extra space/ non-uniformity). Line number : ", "status" : False}
    if(not (isMeterNumberPattern(rowList[0]) and isSevenDigitFloat(rowList[1]) and isSevenDigitFloat(rowList[2]) and isSevenDigitFloat(rowList[3]))) : 

        return {"message" : "Non-uniformity in Meter no./ Active energy/ Reactive high/Reactive low. Line number : ", "status" : False}
    if(not isDate(rowList[4])) :

        return {"message" : "Date format mismatch : "+ str(rowList[4]) +". Line number : ", "status" : False}
    
    return {"message" : "All checked." , "status" : True}
   
def weekHeaderCheck(rowList) :
    
    if(len(rowList) != 11) :
        return {"message" : "Structural error.(Can be Missing data/ extra space/ non-uniformity). Line number : ", "status" : False}
    if(not (rowList[0]=='WEEK' and rowList[1]=='FROM' and rowList[3]=='HRS' and rowList[4]=='OF' and rowList[6]=='TO'and rowList[8]=='HRS'and rowList[9]=='OF')) :
        return {"message" : "Structural error.(Can be Missing data/ extra space/ non-uniformity). Line number : ", "status" : False}
    if(not isTime(rowList[2])) :
        return {"message" : "Timestamp format mismatch : "+ str(rowList[2]) +". Line number : ", "status" : False}
    if(not isTime(rowList[7])) :
        return {"message" : "Timestamp format mismatch : "+ str(rowList[7]) +". Line number : ", "status" : False}
    if(not isDate(rowList[5])) :
        return {"message" : "Date format mismatch : "+ str(rowList[5]) +". Line number : ", "status" : False}
    if(not isDate(rowList[10])) :
        return {"message" : "Date format mismatch : "+ str(rowList[10]) +". Line number : ", "status" : False}
     # If I reach here, I am pretty sure that both the dates are in correct format.
    if(datetime.strptime(rowList[10], "%d-%m-%y") < datetime.strptime(rowList[5], "%d-%m-%y")) :  # <= changed to <
        return {"message" : "Date format mismatch. End date smaller than start date. Line number : ", "status" : False}
    
    return {"message" : "All checked." , "status" : True}

# ************************************************ Helps Real Meter MWH Creation *****************************************

# ************************************************ Helps Fictitious Meter MWH Creation *****************************************

def decideSpace(spaceValue,stringToCheck) :
    spaceOffset = max(spaceValue,len(stringToCheck)+1)
    return spaceOffset - len(stringToCheck)

#############################################################################################################################################