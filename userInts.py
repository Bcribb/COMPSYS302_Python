import cherrypy
import databaseInts
import json
import urllib2
import time
import base64
import mimetypes
import bleach
from helperFunctions import helpers

helpers = helpers()

class UserInts(object):
    _cp_config = {'tools.encode.on': True,
                  'tools.encode.encoding': 'utf-8',
                  'tools.sessions.on': 'True',
                  }

    # When the user clicks the send button we send a message if there was one and/or a file if there was one
    @cherrypy.expose
    def sendThings(self, message=None, inputFile=None):
        try:
            if message:
                self.sendMessage(message)
        except:
            message = 'Didn\'t send message, one likely wasn\'t entered.'
            cherrypy.log(message)
            print helpers.YELLOW + message + helpers.END
        try:
            self.sendFile(inputFile)
        except:
            message = 'Didn\'t send file, one likely wasn\'t attached.'
            cherrypy.log(message)
            print helpers.YELLOW + message + helpers.END
        raise cherrypy.HTTPRedirect('/')

    # Pings the other user and gets their profile
    @cherrypy.expose
    def pingOther(self, person):
        personsProfile = databaseInts.getUser(person)
        user = databaseInts.getUser(cherrypy.session['username'])
        cherrypy.session['profile'] = person
        if user['location'] == personsProfile['location']:
            print helpers.YELLOW + "You're pinging " + person + helpers.END
            try:
                self.sendRequest(person, "ping", {'sender': cherrypy.session['username']})
            except:
                message = 'The ping failed.'
                cherrypy.log(message)
                print helpers.RED + message + helpers.END
            try:            
                dictionary = self.getProfile()
                dictionary['username'] = cherrypy.session['profile']
                databaseInts.addProfile(dictionary)
            except:
                message = 'Failed to get user profile.'
                cherrypy.log(message)
                print helpers.RED + message + helpers.END
        else:
            message = 'You can\'t ping that person as they\'re not on the same network'
            cherrypy.log(message)
            print helpers.RED + message + helpers.END
        raise cherrypy.HTTPRedirect('/')
    
    #sends a message to other users
    @cherrypy.expose
    def sendMessage(self, message):
        print helpers.YELLOW + "You're sending a message to " + cherrypy.session['profile'] + "." + helpers.END
        dictionary = {'sender' : cherrypy.session['username'], 'destination' : cherrypy.session['profile'], \
                      'message' : message, 'stamp' : time.time()}
        answer = self.sendRequest(cherrypy.session['profile'], "receiveMessage", dictionary)
        dictionary['answer'] = answer
        databaseInts.addMessage(dictionary)
        print helpers.BLUE + answer + helpers.END

    # Sends a file to other users
    @cherrypy.expose
    def sendFile(self, inputFile):
        print helpers.YELLOW + "You're sending a file to " + cherrypy.session['profile'] + "." + helpers.END
        unencoded = inputFile.file.read()
        encoded = base64.b64encode(unencoded)
        dictionary = {'sender' : cherrypy.session['username'], 'destination' : cherrypy.session['profile'], \
                      'file' : encoded, 'filename' : inputFile.filename, 'stamp' : time.time(), 'content_type' : mimetypes.guess_type(inputFile.filename)[0]}
        answer = self.sendRequest(cherrypy.session['profile'], "receiveFile", dictionary)
        dictionary['answer'] = answer
        databaseInts.addFile(dictionary)
        print helpers.BLUE + answer + helpers.END

    # updates the user information for their input form
    @cherrypy.expose
    def updateProfile(self, fullname=None, position=None, description=None, picture=None):
        lastUpdated = str(time.time())
        username = cherrypy.session['username']
        currentProfile = {}
        currentProfile = databaseInts.getUser(username)
        dictionary = {'fullname' : fullname, 'position' : position, 'description' : description, 'picture' : picture, 'lastUpdated' : lastUpdated, 'username' : username}
        for element in dictionary:
            if len(dictionary[element]) < 1:
                dictionary[element] = currentProfile[element]
        databaseInts.updateUserProfile(dictionary)
        raise cherrypy.HTTPRedirect('/')     

    # Gets the profile of another user
    @cherrypy.expose
    def getProfile(self):
        print helpers.YELLOW + "You're asking for " + cherrypy.session['profile'] + "s profile, " + cherrypy.session['username'] + helpers.END
        dictionary = {'sender' : cherrypy.session['username'], 'profile_username' : cherrypy.session['profile']}
        returnedDictionary = self.sendRequest(cherrypy.session['profile'], "getProfile", dictionary)
        oldProfile = databaseInts.getUser(cherrypy.session['profile'])
        returnedDictionary = helpers.updateDictionary(oldProfile, returnedDictionary)
        returnedDictionary = helpers.cleanDictionary(returnedDictionary)
        return returnedDictionary

    # Converts a dictionary to json dictionary
    def convertToJson(self, dictionary):
        return json.dumps(dictionary)

    # Reads a jsonObject
    def readJson(self, jsonObject):
        return json.load(jsonObject)

    # Used to send requests to other users
    def sendRequest(self, username, functionName, dictionary):
        user = databaseInts.getUser(username)
        URL = self.getUserURL(user) + "/" + functionName
        jsonDict = self.convertToJson(dictionary)
        if functionName == "ping":
            response = urllib2.urlopen(URL + "?sender=" + cherrypy.session['username'], timeout=3).read()
        else:
            request = urllib2.Request(URL)
            request.add_header('Content-Type', 'application/json')
            try:            
                response = urllib2.urlopen(request, jsonDict, timeout=3)
                if functionName == "getProfile":                
                    response = self.readJson(response)
                    return response
                else:
                    response = response.read()
                    return response
            except:
                message = 'The server failed to respond.'
                cherrypy.log(message)
                print helpers.RED + message + helpers.END
                response = "-1"
        return response

    # Gets the URL of the user from the database
    def getUserURL(self, user):
        if user['username'] == cherrypy.session['username']:
            return "http://localhost:10009"
        ip = user['ip']
        port = user['port']
        return "http://" + ip + ":" + port



