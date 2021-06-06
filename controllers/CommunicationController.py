import requests
import json
from time import gmtime, strftime
import pymsteams

class Comms():

    def __init__(self, teamsStatus, teamsUrl, add_urls):

        self.teamsStatus = teamsStatus
        self.default_url = teamsUrl

        self.add_urls = add_urls
    
    def PostMessage(self, testName, message, fixed=False):
        """ """

        self.testName=testName
        self.message=message

        message = "*" + testName + ":* " + message
        self.originalMessage = message

        now=strftime("%H:%M", gmtime())
        breakline=("-"*10) + now + ("-"*10)
        message = breakline + '\n' + message
        
        message = "**" + self.testName + ":** " + self.message

        self.SendTeamsMessage(message, self.default_url)

        if testName in self.add_urls:
            for url in self.add_urls[testName]['hooks']:
                if not fixed:
                    message = f"{self.add_urls[testName]['error_message']}"
                    self.SendTeamsMessage(message, url)
                else:
                    message = f"{self.add_urls[testName]['resolution_message']}"
                    self.SendTeamsMessage(message, url)

    def SendTeamsMessage(self, message, webhook):

        if self.teamsStatus == "on":
            print(" -Printing to Teams: '" + message + "'")
            myTeamsMessage = pymsteams.connectorcard(webhook)

            myTeamsMessage.text(message)

            myTeamsMessage.send()
