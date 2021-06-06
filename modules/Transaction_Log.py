
import pyodbc

class Transaction_Log():

    def __init__(self, config):
        """Controls processes"""

        self.response = {
            "result": "passed",
            "message": "Blocked processes on: "
        }

        
        self.config=config["Transaction_Log"]
        
        self.dbController = config["dbController"]
        
    def __run__(self):
        """Controls process flow for test, returns the results"""

        results = self.CheckServers()
        errors = {}

        for row in results:
            if row[2] >= self.config["threshold"] and row[0] not in self.config["exceptions"]:
                errors[row[0]] = str(int(row[2]))

        if len(errors)>0:
            self.response["result"]="failed"
            message = "Some databases above transaction log size threshold (" + str(self.config["threshold"]) + "%): "
            for database in errors:
                message += database + " (" + errors[database] + "%)" + ", "
            self.response["message"] = message.rstrip(', ') + "."
        else:
            self.response["result"]="passed"
            self.response["message"]="All databases below threshold."
            
        return( self.response )     


    def CheckServers(self):
        """  """

        results = self.dbController.RunCustomQuery(self.config["query"], self.config["database"])

        return(results)

