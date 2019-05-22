import bleach

#A bunch of helpers functions
class helpers:
    #Colours for ANSI encoding when printing to terminal
    RED = '\033[31m'
    BLUE = '\033[94m'
    YELLOW = '\033[33m'
    END = '\033[0m'

    #Removes HTML from the strings in a dictionary
    def cleanDictionary(self, returnedDictionary):
        for element in returnedDictionary:
            isntNone = returnedDictionary[element] is not None
            isAString = isinstance(returnedDictionary[element], basestring) 
            if isntNone and isAString:
                returnedDictionary[element] = bleach.clean(returnedDictionary[element])
        return returnedDictionary

    #Updates a dictionary with new values of a different dictionary
    def updateDictionary(self, oldDictionary, newDictionary):
        returnDictionary = oldDictionary    
        for element in newDictionary:
            returnDictionary[element] = newDictionary[element]
        return returnDictionary
