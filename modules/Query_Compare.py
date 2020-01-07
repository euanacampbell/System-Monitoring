import sys
import time
from datetime import datetime, timedelta, date
import yaml
import os
import pyodbc

class Query_Compare():

    def __init__(self, config):
        """Controls processes"""

        self.results = []

        self.config = config["Query_Compare"]

        self.response = {}
        
        
    
    def __run__(self):
        """Controls process flow for test, returns the results"""

        self.RunQuery()
        
        self.CheckResults()

        return( self.response ) 


    def RunQuery(self):
        """Connects to server/database, and runs the desired query, putting the results into self.results"""

        connection = pyodbc.connect('DRIVER={' + self.config["driver"] + '}; SERVER=' + self.config["server"] + '; DATABASE=' + self.config["database"] + ';Trusted_Connection=yes;')

        cursor = connection.cursor()
        
        SQLCommand = (self.config["query"])
        
        cursor.execute(SQLCommand)

        self.results = cursor.fetchone()[0]


    def CheckResults(self):
        """Iterates through self.results and checks that all systems are Active - Determines whether a failure has occurred."""
        
        if self.results > 0:
            self.response["result"] = "passed"
            self.response["message"] = str(self.results) + " portfolio valuations have been generated today."
        elif self.results == 0 and date.today().weekday() == 0:
            self.response["result"] = "passed"
            self.response["message"] = "No portfolios valuations expected to be generated on Mondays."
        else:
            self.response["result"] = "failed"
            self.response["message"] = "No portfolio valuations have been generated today, investigation required."