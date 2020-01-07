import pyodbc
import yaml

class Error_Checking():

    def __init__(self, config):
        """Sets up variables"""

        self.config = config["Error_Checking"]
        self.secret = config["decrypted"]

    def __run__(self):
        """Controls process flow for test, returns the results"""

        results = self.RunQuery()

        response = self.CheckResults(results)

        return( response ) 


    def RunQuery(self):
        """Connects to server/database, and runs the desired query, putting the results into self.results"""

        # Connection properties
        connection = pyodbc.connect('DRIVER={' + self.config["driver"] + '}; SERVER=' + self.config["server"] + '; DATABASE=' + self.config["database"] + ';UID=' + self.secret["idm_username"] + '; PWD=' + self.secret["idm_password"])

        cursor = connection.cursor()
        SQLCommand = self.config["query"] # gets the query from the config
        cursor.execute(SQLCommand) # performs query

        return( cursor.fetchall() )


    def CheckResults(self, results):
        """Iterates through self.results and checks that all systems are Active - Determines whether a failure has occurred. Creates the response."""
        
        response = {}
        if len(results) == 0:
            response["result"] = "passed"
            response["message"] = "No unresolved API errors."
        else:
            response["result"] = "failed"
            results = results[0]
            api = results[2].split("RestClient")[0]
            endpoint = results[3].split("/")[-1]
            time = results[1][0:19]
            
            message = "%s/%s at %s." % (api, endpoint, time)
            print(message)
            response["message"] = message
        
        response["testName"] = self.config["testname"]

        return( response )


if __name__ == '__main__':
    run = Error_Checking(yaml.safe_load(open('..\config.yaml')))
    print( run.__run__() )