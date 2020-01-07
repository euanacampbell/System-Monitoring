from selenium import webdriver
import sys
import time
from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta

class Selenium_Example():

    def __init__(self, config):
        """Controls processes"""

        self.username = config["decrypted"]["username"]
        self.password = config["decrypted"]["password"]

        self.chromePath = config["chromedriver_path"]

        self.reports = []  #[reportName, hasRun]
        self.response = {}
        self.response["result"] = "passed"
        self.response["message"] = "" 
        self.countIssues = 0
    
    def __run__(self):
        # Stops driver from loading physical browser
        options = webdriver.ChromeOptions()
        options.add_argument("headless")

        # Initialises browser
        self.driver = webdriver.Chrome(executable_path=self.chromePath, chrome_options=options)

        self.Login()

        self.GoToScheduledReports()

        self.PullReportsInfo()

        self.driver.quit()

        return( self.response )

    def Login(self):
        self.driver.get('URL') # Go to Exact

        inputusername = self.driver.find_element_by_id("ID")    # Find username field
        inputusername.send_keys(self.username)  # Enter username

        inputPassword = self.driver.find_element_by_id("ID")  # Find password field
        inputPassword.send_keys(self.password)  # Enter password

        self.driver.find_element_by_name('NAME').click()  # Clik on login button
        


    def GoToScheduledReports(self):
        self.driver.find_element_by_xpath('XPATH').click()

    
    def PullReportsInfo(self):

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        data = []
        table = soup.find('table')
        table_body = table.find('tbody')

        rows = table_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            data.append([ele for ele in cols if ele]) # Get rid of empty values

        data.pop(0)

        
        for i in data:
            try:
                if "(Generation Incomplete)" in i[2]:
                    self.response["result"] = "failed"
                    self.countIssues += 1
                    self.response["message"] += "Generation Incomplete: " + i[0] + ". "
                    continue
            except:
                pass
        
        if self.countIssues == 0:
            self.response["message"] = "All reports generated successfully."
            