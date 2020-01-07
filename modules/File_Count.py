import sys
import time
from datetime import datetime, timedelta, date
import yaml
import os
import pyodbc

class File_Count():

    def __init__(self, config):
        """Controls processes"""

        self.config = config["File_Count"]

        self.results = []

        self.numOfFiles = 0

        self.response = {}
        
        
    
    def __run__(self):
        """Controls process flow for test, returns the results"""

        self.Count()

        return( self.response ) 


    def Count(self):
        """  """
        try:
            for name in os.listdir("\\\\" + self.config["path"]):
                if name.endswith(".CSV") or name.endswith(".txt") or name.endswith(".txt"):
                    self.numOfFiles += 1
        except FileNotFoundError:
            self.response["result"] = "failed"
            self.response["message"] = "Unable to access " + self.config["path"]
            return()

        if self.numOfFiles > self.config["filelimit"]:
            self.response["result"] = "failed"
            self.response["message"] = str(self.numOfFiles) + " files on oct-mi01. Check VCTDataImport SSIS package ran successfully."
            return()
        else:
            self.response["result"] = "passed"
            self.response["message"] = "No files waiting to be processed."