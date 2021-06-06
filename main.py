from imports.module_imports import *
from imports.system_imports import *

import cProfile
import re


class Controller():

    def __init__(self):
        """Loads all modules from /modules | Loads config"""
        
        # Load modules
        self.modules = self.GetModules()

        # Load config
        self.GetConfigs()

        # Get current user
        self.currentUser = getpass.getuser()

        # Determine whether to run against test or Live Database
        self.environment = self.LiveOrTest(self.config["environment"], self.currentUser)
        print("\nEnvironment: " + self.config["environment"].title() + "\n")

        # Create database controller
        #self.Database = Database(self.config[self.environment + "_connections"])
        self.Database = Database(self.config, self.environment)

        # Create communication controller
        self.Comms = Comms(self.config["teams_toggle"], self.config["teams-connectors"][self.environment], self.config["alternative_webhooks"])

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
        
        self.Database.LogEvent("General", "START")
        self.RunTests()
        self.Database.LogEvent("General", "END")


    def RunTests(self):
        """Runs all tests from /modules"""

        response = {}
        testName = ""

        # For all the modules we want to run
        for i in self.modules:

            if i in globals() and self.allowed_to_run(i): 
                testName = i.replace("_", " ")


                # Reloads config
                self.GetConfigs() # Reloads config
                self.config["dbController"]=self.Database
                encrypted = self.Database.GetEncryptedPasswords() # Get encrypted values
                self.config["decrypted"] = self.encryption.DecryptPasswords(encrypted)

                test = globals()[i](self.config)   # Initialise the test (will run __init__() from module)
                print(  "\n•" + testName )
                
                try:
                    # Catches change of environment during run-time
                    if self.config["environment"] != self.environment:
                        print("cheeky, you can't do that")
                        break
                    self.Database.LogEvent(testName, "Starting")
                    response = test.__run__()   # RUNS THE TEST HERE
                    response["testName"] = testName
                    self.Database.LogEvent(testName, "Completed: " + response['result'])
                    print(" -" + response['result'] + ": " + response['message'])

                    self.CheckResults(response)
                    
                except:
                    # Test failed to complete
                    print(" -Test failed to run successfully")
                    print(traceback.format_exc())
                    self.Database.LogEvent(testName, str( traceback.format_exc() ).replace("'", "''") )

                    formatted_error = traceback.format_exc().splitlines()[-1] + "."

                    response = {}

                    response["testName"] = testName
                    response["message"] = "Test failed to run successfully - " + formatted_error
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


    def GetConfigs(self):

        root_dir = os.path.abspath(os.path.dirname(__file__))

        try:
            yaml_path = os.path.join(root_dir+'\configs', 'modules_config.yaml')
            modules_config = yaml.safe_load(open(yaml_path))

            yaml_path = os.path.join(root_dir+'\configs', 'system_config.yaml')
            system_config = yaml.safe_load(open(yaml_path))
        except:
            print("Unable to open a config, check modules_config.yaml and system_config.yaml")
            traceback.print_exc()
            sys.exit(0)
        
        # Merges configs to create a single one
        self.config = {**modules_config, **system_config}
    
    def CheckResults(self, response):
        """Identifies what to do with the result from the test, acting accordingly."""

        lastResult = self.Database.GetLastResult(response["testName"])
        lastMessage = self.Database.GetLastMessage(response["testName"])

        # What do to based on each failure combination from previous test run
        if lastResult == None and response["result"] == "failed": # New test
            response["message"] = self.RaiseTicket(response)
            self.Comms.PostMessage(response["testName"], response["message"])
        elif lastResult == None and response["result"] == "passed": # New test
            pass
        else:
            # Issue now fixed
            if lastResult == "failed" and response["result"] == "passed":
                response["message"] = "Issue has been fixed."
                self.Comms.PostMessage(response["testName"], response["message"], fixed=True)
            # If still failing, but message is different
            elif (
                lastResult == "failed"
                and response["result"] == "failed"
                and response['message'] != lastMessage.split(" Jira ticket: OSD")[0]
                and 'message format cannot be inserted into database' not in lastMessage.split(" Jira ticket: OSD")[0]
            ):
                self.Comms.PostMessage(response["testName"], response["message"])
            # If test fails for the first time
            elif lastResult == "passed" and response["result"] == "failed":
                response["message"] = self.RaiseTicket(response)
                self.Comms.PostMessage(response["testName"], response["message"])

        # Record result in database
        self.Database.RecordResult(
            response["testName"], response["message"], response["result"]
        )

    def RaiseTicket(self, response):
        
        if self.config["jira_toggle"] == "on" and self.config["environment"]=="live":
            failures = int(self.Database.GetRecentFailures(response)) # Gets how many times the test has failed recently

            if failures == 0 and "Issue has been fixed" not in response["message"]:
                print("Longer than 3 hours, raising Jira ticket")
                self.Database.LogEvent("General", "Raising Jira ticket.")
                ticketNumber = self.jira.RaiseTicket(response["testName"], response["message"] )
                message = response["message"] + " Jira ticket: " + str(ticketNumber) + "."
            else:
                print("-Not raising Jira ticket, not long enough since last error")
                self.Database.LogEvent("General", "Not raising Jira ticket, not long enough since last error")
                message = response["message"]
        else:
            self.Database.LogEvent("General", "Jira toggle is off or running in test environment")
            message = response["message"]
        return(message)
        

    def allowed_to_run(self, module):
        """Based on the inputs tells the runtime whether the check should run"""
        exceptions=self.config["runtime"]["exceptions"]
        default=self.config["runtime"]["default"]
        timeNow = str( datetime.now().time() )

        if module in self.config["runtime"]["exceptions"]:
            self.Database.LogEvent(module, "Running with specialist times")
            bankholidays=exceptions[module]["bankholidays"]
            starttime=exceptions[module]["starttime"]
            endtime=exceptions[module]["endtime"]
            days_to_not_run_on=exceptions[module]["days_to_not_run_on"]
        else:
            self.Database.LogEvent(module, "Running with default times")
            bankholidays=default["bankholidays"]
            starttime=default["starttime"]
            endtime=default["endtime"]
            days_to_not_run_on=default["days_to_not_run_on"]

        # Time Check
        if timeNow > endtime or timeNow < starttime:
            self.Database.LogEvent(module, "Not set to run at this time")
            return(False)

        dayLookup = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6}
        # Day Check
        for i in days_to_not_run_on:
            if date.today().weekday() == dayLookup[i]:
                self.Database.LogEvent(module, "Not set to run today")
                return(False)
        
        # Bank Holiday Check
        if date.today() in holidays.England() and bankholidays=="No":
            self.Database.LogEvent(module, "Not set to run on a bank holiday")
            return(False)

        return(True)
    
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
            if self.config["jira_toggle_testoverride"]!="on": # Turn off ticket creation when running in test environment
                self.config["jira_toggle"] = "off" 
            if user in self.config["test_users"]:  # if they have access to test
                return "test"
            else:
                message = "Access denied for: " + self.currentUser
                print(message)
                sys.exit(0)
        else:
            message = "Environment from config not recognised"
            print(message)
            sys.exit(0)


        
if __name__ == '__main__':

    if len(sys.argv) > 1:
        if sys.argv[1] == "endless":
            print("\nStart mode: Endless")
            while True:
                run=Controller()
        elif sys.argv[1] == "profile":
            print("\nStart mode: Profile")
            cProfile.run('Controller()')
        else:
            print("Start mode not recognised.")
            sys.exit(0)
    else:
        print("\nStart mode: Once")
        run=Controller()