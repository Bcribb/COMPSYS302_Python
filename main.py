import urllib2
import base64
import cherrypy
import codecs
import csv
import loginServer
import templater
import userInts
import socket
import databaseInts
from helperFunctions import helpers

helpers = helpers()
listen_ip = "0.0.0.0"
listen_port = 10009
urlName = 'http://cs302.pythonanywhere.com/'

class MainApp(object):
    _cp_config = {'tools.encode.on': True,
                  'tools.encode.encoding': 'utf-8',
                  'tools.sessions.on': 'True',
                  }

    # If they try somewhere we don't know, catch it here and send them to the right place.
    @cherrypy.expose
    def default(self, *args, **kwargs):
        """The default page, given when we don't recognise where the request is for."""
        Page = "404 Page not found."
        cherrypy.response.status = 404
        return Page

    # PAGES (which return HTML that can be viewed in browser)
    @cherrypy.expose
    def index(self):
        #Returns the main page if someone is logged in        
        try:
            if cherrypy.session['username'] == cherrypy.session['profile']:
                isUsersPage = True
            else:
                isUsersPage = False
            dictionary = {'username' : cherrypy.session['username'], 'password' : cherrypy.session['password'],
                          'profile': cherrypy.session['profile'], 'isUsersPage' : isUsersPage}
            page = templater.templateMainPage(codecs.open("html/welcomePage.html").read(), dictionary, loginServer. getList())
        except KeyError:  # There is no username
            raise cherrypy.HTTPRedirect('/loginServer/login')
        return page

    # For others to ping me (always returns 0)
    @cherrypy.expose
    def ping(self, sender):
        print helpers.BLUE + sender + " pinged you" + helpers.END
        return "0"

    # When others ask for someones profile I return it (returns profile on success)
    @cherrypy.expose
    @cherrypy.tools.json_in()
    def getProfile(self):
        data = cherrypy.request.json
        print helpers.BLUE + data['sender'] + " asked for " + data['profile_username'] + "s profile" + helpers.END
        userProfile = databaseInts.getUserProfile(data['profile_username'])
        return userProfile
    
    # When others send me a message (returns 0... when successsful)
    @cherrypy.expose
    @cherrypy.tools.json_in()
    def receiveMessage(self):
        data = cherrypy.request.json
        print helpers.BLUE + data['sender'] + " sent you a message." + helpers.END
        data = helpers.cleanDictionary(data)
        data['answer'] = "0: <Action was successful>"
        if data['sender'] is not data['destination']:
            databaseInts.addMessage(data)
        return "0: <Action was successful>"

    # When others send me a file (returns 0... when successful)
    @cherrypy.expose
    @cherrypy.tools.json_in()
    def receiveFile(self):
        data = cherrypy.request.json
        print helpers.BLUE + data['sender'] + " sent you a File." + helpers.END
        data = helpers.cleanDictionary(data)
        data['answer'] = "0: <Action was successful>"
        if data['sender'] is not data['destination']:
            databaseInts.addFile(data)
        encodedFile = data['file']
        filename = data['filename']
        self.decodeAndWrite(encodedFile, filename)
        return "0: <Action was successful>"

    # Decodes a base 64 encoded string and writes it to a file in static
    def decodeAndWrite(self, encodedFile, filename):
        decoded = base64.b64decode(encodedFile)
        newFile = codecs.open("static/" + filename, "w")
        newFile.write(decoded)
        newFile.close()

def runMainApp():
    # Create an instance of MainApp and tell Cherrypy to send all requests under / to it. (ie all of them)
    cherrypy.tree.mount(MainApp(), "/")
    cherrypy.tree.mount(loginServer.LoginServer(), "/loginServer/")
    cherrypy.tree.mount(userInts.UserInts(), "/userInts/")
    # Tell Cherrypy to listen for connections on the configured address and port.
    cherrypy.config.update({'server.socket_host': listen_ip,
                            'server.socket_port': listen_port,
                            'engine.autoreload.on': True,
                            'tools.staticdir.on' : True,
                            'tools.staticdir.dir' : "/static",
                            'log.error_file': "errors.log",
                            'log.access_file': "access_file.log"
                            })
    print "Running Blain's Project"

    # Start the web server
    cherrypy.engine.start()

    # And stop doing anything else. Let the web server take over.
    cherrypy.engine.block()

# Run the function to start everything
runMainApp()







