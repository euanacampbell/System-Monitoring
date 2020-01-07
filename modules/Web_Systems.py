from selenium import webdriver
import sys
import time
from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
#import EncryptionController

class Web_Systems():

    def __init__(self, config):
        """Controls processes"""
    
        self.systems = config["Web_Systems"]

        self.response = {}
        self.response["result"] = "passed"
        
        self.response["message"] = "All systems online."
        self.failedSystems = ["Failed for "]

    def __run__(self):
        
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

        for system in self.systems["automated"]:
            try:
                response = requests.get(self.systems["automated"][system], headers=headers)
                statuscode = response.status_code
                if statuscode != 200:
                    self.response["result"] = "failed"
                    self.failedSystems.append(system)
            except:
                self.response["result"] = "failed"
                self.failedSystems.append(system)

        #self.Novus()
        #self.Watson()
        #self.Oasys()
        #self.Jira()
        #self.WebManager()
        #self.IDM()

        if self.response["result"] == "failed":
            self.response["message"] = " ".join(self.failedSystems)

        return( self.response )