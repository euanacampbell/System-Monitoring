import wmi
from datetime import datetime

class Application_Services():

    def __init__(self, config):
        """Controls processes"""

        self.config = config["app-services"]

        self.response = {}
        
        self.response["message"] = ""
        self.response["output"] = ""
        self.response["result"] = "passed"
        
    
    def __run__(self):
        """Controls process flow for test, returns the results"""

        self.RunScript()

        if self.response["result"] == "passed":
            self.response["message"] = "All application services are running. No action required."
        else:
            self.response["message"] += "Check whether applications are working."

        return( self.response ) 


    def RunScript(self):
        """"""
        for application in self.config["services"]: # For each application
            print( "Application: " + application )
            for server in self.config["services"][application]: # For each server
                print("-Server: " + server)

                # Set up connection properties
                connection = wmi.connect_server(server=server, user=self.config["adminUsername"], password=self.config["adminPassword"])

                # Connect to server
                c = wmi.WMI(wmi=connection)

                actualServices = []

                # Collect all services on server
                for i in c.Win32_Service():
                    actualServices.append( i.Name )
                
                # Check services exist
                for service in self.config["services"][application][server]:
                    if service not in actualServices:
                        self.response["result"] = "failed"
                        self.response["message"] += "\nCannot find: " + application + " | " + server + " | " + service + ". "
                
                timeNow = str( datetime.now().time() )
                
                # For each service
                for service in c.Win32_Service():
                    # If service has an exception
                    if service.Name in self.config["services-exceptions"]:
                        if timeNow > self.config["services-exceptions"][service.Name]["start"] and timeNow < self.config["services-exceptions"][service.Name]["end"]:
                            print("Skipping: " + str( service.Name ))
                            self.response["message"] += service.Name + ": Caught as exception from config."
                            continue
                            
                    # If service in list of services
                    if service.Name in self.config["services"][application][server]:
                        if service.State != "Running": 
                            self.response["message"] += "\n" + application + " | " + server + " | " + service.Name + " | " + service.State + ". "
                            self.response["result"] = "failed"

                        self.response["output"] += application + " | " + server + " | " + service.Name + " | " + service.State + ". "
        

        