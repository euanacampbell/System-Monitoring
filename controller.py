from system_modules.imports import *

class Controller():

    def __init__(self):
        """Loads all modules from /modules | Loads config"""
        
        # Load modules
        self.modules = self.GetModules()

        # Load config
        self.config = self.GetConfig()

        # Get current user
        self.currentUser = getpass.getuser()

        # Determine whether to run against test or Live Database
        self.environment = self.LiveOrTest(self.config["environment"], self.currentUser)
        print("Running: " + self.config["environment"])

        # Create database controller
        self.Database = Database(self.config[self.environment + "_connections"])

        # Create communication controller
        self.Comms = Comms(self.config["slack-webhooks"][self.environment],self.config["slack_toggle"])

        # Load max session ID + increment
        lastSessionId = self.Database.GetLastSessionId()
        self.Database.sessionId = lastSessionId + 1

        self.Database.LogEvent("General", "Running as: " + self.currentUser)

        # Load encrypted passwords and decrypt them + add them to the config
        self.encryption = Encryption()
        encrypted = self.Database.GetEncryptedPasswords() # Get encrypted values
        self.config["decrypted"] = self.encryption.DecryptPasswords(encrypted)

        # Used for Jira integration
        self.jira = JiraController(self.config["decrypted"]["jira_username"], self.config["decrypted"]["jira_password"])

        # Quit running if not between specific times
        self.NeedToQuit()
        

        self.Database.LogEvent("General", "START")
        self.RunTests()
        self.Database.LogEvent("General", "END")


    def RunTests(self):
        """Runs all tests from /modules"""

        response = {}
        testName = ""

        # For all the modules we want to run
        for i in self.modules:
            # Find module in globals (globals allows for dynamically calling functions (can't from string))
            if i in globals():
                testName = i.replace("_", " ")
                self.testfailure = False

                self.Database.LogEvent(testName, "Initialising")
                test = globals()[i](self.config)   # Initialise the test (will run __init__() from module)
                print(  testName )
                
                try:
                    self.Database.LogEvent(testName, "Starting")
                    response = test.__run__()   # RUNS THE TEST HERE
                    response["testName"] = testName
                    self.Database.LogEvent(testName, "Completed")

                    self.Database.LogEvent(testName, "Result: " + response['result']) # Log result
                    self.CheckResults(response)
                    
                except:
                    # Test failed to complete
                    print("-Test failed to run successfully")
                    self.testfailure = True
                    self.Database.LogEvent(testName, str( traceback.format_exc() ).replace("'", "''") )

                    response = {}

                    response["testName"] = testName
                    response["message"] = "Test failed to run successfully"
                    response["result"] = "failed"

                    self.Database.LogEvent(testName, "Result: " + response['result']) # Log result
                    self.CheckResults(response)


    def GetModules(self):

        # Load modules
        filesInDirectory = []
        for (filenames) in os.walk("modules"):
            filesInDirectory.extend(filenames[2])
            break

        modules = []
        for fileName in filesInDirectory:
            modules.append( fileName[:-3] )

        return( modules )


    def GetConfig(self):

        root_dir = os.path.abspath(os.path.dirname(__file__))

        # Connect to config file
        try:
            yaml_path = os.path.join(root_dir, 'config.yaml')
            config = yaml.safe_load(open(yaml_path))
            return( config )
        except:
            print("UNABLE TO OPEN CONFIG")
            sys.exit(0)
    
    def CheckResults(self, response):
        """Identifies what to do with the result from the test, acting accordingly."""

        lastResult = self.Database.GetLastResult(response["testName"])
        lastMessage = self.Database.GetLastMessage(response["testName"])        

        # What do to based on each failure combination from previous test run
        if lastResult == None and response["result"] == "failed": # New test
            response["message"] = self.RaiseTicket(response)
            self.Comms.PostToSlack(response["testName"], response["message"])
        elif lastResult == None and response["result"] == "passed": # New test
            pass
        else:
            # Issue now fixed
            if lastResult == "failed" and response["result"] == "passed":
                response["message"] = "Issue has been fixed."
                self.Comms.PostToSlack(response["testName"], response["message"])
            # If still failing, but message is different
            elif (
                lastResult == "failed"
                and response["result"] == "failed"
                and response['message'] not in lastMessage
            ):
                self.Comms.PostToSlack(response["testName"], response["message"])
            # If test fails for the fist time
            elif lastResult == "passed" and response["result"] == "failed":
                response["message"] = self.RaiseTicket(response)
                self.Comms.PostToSlack(response["testName"], response["message"])

        # Record result in database
        self.Database.RecordResult(
            response["testName"], response["message"], response["result"]
        )

    def RaiseTicket(self, response):
        if self.config["jira_toggle"] == "on":
            failures = int(self.Database.GetRecentFailures(response)) # Gets how many times the test has failed recently

            if failures == 0 and "Issue has been fixed" not in response["message"]:
                self.Database.LogEvent("General", "Raising Jira ticket.")
                ticketNumber = self.jira.RaiseTicket(response["testName"], response["message"] )
                message = response["message"] + " Jira ticket: " + str(ticketNumber) + "."
            else:
                print("-Not raising Jira ticket, not long enough since last error")
                self.Database.LogEvent("General", "Not raising Jira ticket, not long enough since last error")
                message = response["message"]
        else:
            message = response["message"]
        return(message)
        

    def NeedToQuit(self):
        timeNow = str( datetime.now().time() )

        # Stop program if not between the specific times from the config
        if timeNow > self.config["endtime"] or timeNow < self.config["starttime"]:
            message = "Quitting due to time retrictions. Starts: " + self.config["starttime"] + ", Ends: " + self.config["endtime"]
            self.Database.LogEvent("General", message)
            sys.exit(0)

        dayLookup = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6}
        
        # Stops program if not an excluded day from the config
        for i in self.config["days_to_not_run_on"]:
            if date.today().weekday() == dayLookup[i]:
                message = "Quitting due to day restriction for " + i
                self.Database.LogEvent("General", message)
                sys.exit(0)
    
    def LiveOrTest(self, trigger, user):
        """checks what kind of access the user is trying, quits if they do not have access"""

        # Results and Environment database
        if trigger == "live":  # Try to run in live
            if user in self.config["live_users"]:  # if they have access to live
                return "live"
            else:
                message = "Access denied for: " + self.currentUser
                print(message)
                sys.exit(0)
        elif trigger == "test":  # Try to run in test
            if user in self.config["test_users"]:  # if they have access to test
                return "test"
            else:
                message = "Access denied for: " + self.currentUser
                print(message)
                sys.exit(0)
        else:
            message = "Environment from config not recognised"
            print(message)
            self.Database.LogEvent("General", message)
            sys.exit(0)


        
if __name__ == '__main__':

    run = Controller()

    