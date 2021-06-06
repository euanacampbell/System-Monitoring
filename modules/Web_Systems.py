from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import sys
import time
from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta

#import EncryptionController

class Web_Systems():

    def __init__(self, config):
        """Controls processes"""
    
        self.systems = config["web-systems"]

        self.response = {}
        self.response["result"] = "passed"
        
        self.response["message"] = "All systems online."
        self.failedSystems = ["Failed for "]

    def __run__(self):

        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

        for system in self.systems:
            failed_count=0
            for loop in range(0,3):
                try:
                    response = requests.get(self.systems[system], headers=headers, timeout=60)
                    statuscode = response.status_code
                    if statuscode != 200:
                        failed_count+=1
                except:
                    failed_count+=1
            
            if failed_count==3:
                self.response["result"] = "failed"
                self.failedSystems.append(system)


        if self.response["result"] == "failed":
            self.response["message"] = " ".join(self.failedSystems)

        return( self.response )


        