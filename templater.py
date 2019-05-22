import jinja2
import databaseInts
import collections
import codecs
import time

# Template the main page to display everything
def templateMainPage(inputPage, dictionary, listOfUsers):
    listString = ""
    # Makes an attractive list of users
    for person in listOfUsers:
        listString += createListElement(person)
    dictionary['users'] = listString
    userProfile = ""
    currentProfile = databaseInts.getUser(dictionary['profile'])
    #Put a picture if there is one
    if currentProfile['picture'] is not None:
        userProfile += "<img id='profilePic' src=" + currentProfile['picture'] + " alt=" + currentProfile['username'] \
                       + "'s Display pic" + "><br><br>"
    info = collections.OrderedDict()
    info['fullname'] = 'Full Name'
    info['position'] = 'Position'
    info['description'] = 'Description'
    # Displays the users other profile info
    for key, value in info.items():
        userProfile += "<b>" + value + ":</b> "
        if currentProfile[key] is not None:
            userProfile += currentProfile[key]
        else:
            userProfile += 'Hasn\'t been added yet'
        userProfile += '<br>'
    # If were on our own profile let them update things
    if dictionary['isUsersPage']:
        userProfile += createUserProfile()
    messagesDictionary = databaseInts.getMessages(dictionary)
    messages = ""
    # add the messages
    for number in range(len(messagesDictionary)):
        messages += createMessage(messagesDictionary[number], dictionary['username'], dictionary['profile'])
    dictionary['messages'] = messages
    dictionary['profile'] = userProfile
    template = jinja2.Template(inputPage)
    return template.render(dictionary)

# Template the list.html file to show users on the left
def createListElement(person):
    fileLink = codecs.open("html/listElement.html").read()
    template = jinja2.Template(fileLink)
    return template.render(person=person)

# Reads the information for showing update profile buttons
def createUserProfile():
    fileLink = codecs.open("html/userProfile.html").read()
    return fileLink

# Templates the message html file for displaying
def createMessage(messageDict, user, profile):
    tempDict = {}
    # Displays time if it was sent correctly, or a message if it failed
    if messageDict['answer'] is not None:
        if messageDict['answer'][0] == "0":
            tempDict['wasSent'] = ""
            tempDict['timestamp'] = time.strftime('%d-%m-%Y %H:%M:%S', time.localtime(float(messageDict['stamp'])))
        else:
            tempDict['wasSent'] = "style=\"background-color:red\""
            tempDict['timestamp'] = "Message failed to send"
    else:
        tempDict['wasSent'] = ""
        tempDict['timestamp'] = time.strftime('%d-%m-%Y %H:%M:%S', time.localtime(float(messageDict['stamp'])))
    first,second = messageDict['messageID'].split(":")
    mainUser = databaseInts.getUser(user)
    otherProfile = databaseInts.getUser(profile)
    # logic for differences between sender and receiver css
    if first == user:
        tempDict['whichUser'] = ""
        tempDict['image'] = mainUser['picture']
        tempDict['rol'] = "right"
        tempDict['rolOpposite'] = "left"
    else:
        tempDict['whichUser'] = " darker"
        tempDict['image'] = otherProfile['picture']
        tempDict['rol'] = "left"
        tempDict['rolOpposite'] = "right"
    if messageDict['contentType'] == "plain/text":
        tempDict['message'] = messageDict['message']
    else:
        fileLink = codecs.open("html/fileLink.html").read()
        fileTemp = jinja2.Template(fileLink)
        fileTemp = fileTemp.render(filename=messageDict['message'])
        tempDict['message'] = fileTemp
    returnString = codecs.open("html/message.html").read()
    template = jinja2.Template(returnString)
    return template.render(tempDict)


