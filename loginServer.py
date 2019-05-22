import cherrypy
import codecs
from Crypto.Hash import SHA256
import urllib2
import json
import databaseInts
import socket

urlName = 'http://cs302.pythonanywhere.com/'

# This class handles all interactions with the login server.
class LoginServer(object):

    _cp_config = {'tools.encode.on': True,
                  'tools.encode.encoding': 'utf-8',
                  'tools.sessions.on': 'True',
                  }

    # Simply returns the login page when requested
    @cherrypy.expose
    def login(self):
        Page = codecs.open("html/loginPage.html")
        return Page.read()

    # Used to sign in to the login server
    @cherrypy.expose
    def signin(self, username=None, password=None, location=0):
        # Hashing using SHA256
        hashedPassword = hashPassword(password, username)
        error = self.authoriseUserLogin(username, hashedPassword, location)
        # If we successfully login continue else redirect to login
        if error == 0:
            cherrypy.session['username'] = username;
            cherrypy.session['password'] = hashedPassword;
            cherrypy.session['profile'] = username;
            raise cherrypy.HTTPRedirect('/')
        else:
            raise cherrypy.HTTPRedirect('/')

    # Check the users credentials with the login server
    def authoriseUserLogin(self, username, password, location):
        if location == "2":
            ip = urllib2.urlopen("http://ip.42.pl/raw").read()
        else:
            ip = socket.gethostbyname(socket.gethostname())
        print ip
        if username == "bcri429":
            port = '10009'
        enc = '0'
        inputs = 'username=' + username + '&password=' + password + \
                 '&location=' + location + '&ip=' + ip + '&port=' + \
                 port + '&enc=' + enc
        errorCode = urllib2.urlopen(urlName + "report", inputs).read()[0]
        print errorCode
        if errorCode == '0':
            return 0
        else:
            return 1

    # Sends the signout request to the login server
    @cherrypy.expose
    def signout(self):
        """Logs the current user out, expires their session"""
        username = cherrypy.session.get('username')
        password = cherrypy.session.get('password')
        if (username == None):
            errorCode = "No one is logged on"
        else:
            inputs = 'username=' + username + '&password=' + password + '&enc=0'
            errorCode = urllib2.urlopen(urlName + "logoff", inputs).read()
        if errorCode[0] == '0':
            cherrypy.lib.sessions.expire()
            raise cherrypy.HTTPRedirect('/loginServer/login')
        else:
            raise cherrypy.HTTPRedirect('/')

# Gets the online userlist form the login server
def getList():
    userList = []
    inputs = 'username=' + cherrypy.session.get('username') + '&password=' + cherrypy.session.get('password') + \
             '&enc=0' + '&json=1'
    returnedFile = urllib2.urlopen(urlName + "getList", inputs)
    returnedFile = json.load(returnedFile)
    for person in returnedFile:
        databaseInts.addToUsers(returnedFile[person])
        if not returnedFile[person]['username'] in userList:
            userList.append(returnedFile[person]['username'])
    return userList

# Hashes password using SHA256 with username as a salt
def hashPassword(password, username):
    hashedPassword = SHA256.new()
    hashedPassword.update(password + username)
    return hashedPassword.hexdigest()
