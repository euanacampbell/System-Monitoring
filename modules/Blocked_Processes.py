
import pyodbc

class Blocked_Processes():

    def __init__(self, config):
        """Controls processes"""

        self.response = {
            "result": "passed",
            "message": "Blocked processes on: "
        }

        self.uniqueservers = self.GetUniqueServers(config["db_connections"])
        self.dbConnections=config["db_connections"]
        
        self.query=config["Blocked_Processes"]["query"]
        
        self.dbController = config["dbController"]
        
    def __run__(self):
        """Controls process flow for test, returns the results"""

        results = self.CheckServers(self.uniqueservers)

        if len(results) == 0:
            self.response["result"]="passed"
            self.response["message"]="No blocked processes."
        else:
            self.response["result"]="failed"
            self.response["message"]=self.CreateMessage(results)

        return( self.response ) 


    def CheckServers(self, servers):
        """  """
        blockedServers={}
        for server in servers:
            results = self.dbController.RunCustomQuery(self.query, self.LookupServer(server))
            formatted = self.dbController.Fetchone(results)       
            if formatted > 0:
                blockedServers[server]=formatted

        return(blockedServers)

    def LookupServer(self, server):
        """get first db with server from input"""
        
        for i in self.dbConnections:
            if self.dbConnections[i]["server"]==server:
                return(i)

    def GetUniqueServers(self, connections):
        
        uniqueServers = []

        for i in connections:
            if connections[i]["server"] not in uniqueServers:
                uniqueServers.append(connections[i]["server"])

        return(uniqueServers)
    
    def CreateMessage(self, blocked):
        message=""
        for i in blocked:
            message+=str(blocked[i]) + " on " + i + "=" + ", "

        message = message[:-2] # Removes final comma

        return(message)