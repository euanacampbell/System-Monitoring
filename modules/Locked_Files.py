import os
from os.path import isfile, join
import time
import traceback

class Locked_Files():

    def __init__(self, config):
        """Controls processes"""

        self.config = config["Locked_Files"]

        self.results = []

        self.numOfFiles = 0

        self.response = {}

    def __run__(self):
        """Controls process flow for test, returns the results"""

        self.Count()

        return( self.response ) 


    def Count(self):
        """  """

        lockedFiles = []
        for location in self.config["locations"]:
            
            now = time.time()
            allMsgs = [f for f in os.listdir(location) if isfile(join(location, f)) and ".db" not in f and os.stat(join(location, f)).st_mtime < now - int(self.config["creation_delay"])*60]
            print(allMsgs)
            for file_ in allMsgs:
                file_path=location + f"/{file_}"
                
                # if you're reading this, I'm sorry for the mess below that is the try/except within a try/except
                # attempts to open the file, if it thinks it is locked, it will try again after X seconds (re_attempt_delay). Only if it locks twice will it fail.
                if isfile(file_path):
                    try:
                        myfile = open(file_path, "r+") # or "a+", whatever you need
                    except IOError:
                        time.sleep(self.config["re_attempt_delay"])

                        if isfile(file_path):
                            try:
                                myfile = open(file_path, "r+") # or "a+", whatever you need
                            except IOError:
                                self.response["result"] = "failed"
                                self.response["message"] = file_path
                                print(traceback.format_exc())
                                return()
        
        # No locked file found so return a pass  
        self.response["result"] = "passed"
        self.response["message"] = "No locked files."