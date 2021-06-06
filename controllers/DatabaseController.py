import pyodbc
from datetime import datetime

class Database():

    def __init__(self, config, environment):

        self.masterConfig = config
        self.config = config["connections"]
        self.environment = environment
    
    def CreateConnection(self):
        connection = pyodbc.connect('DRIVER={' + self.config["driver"] + '}; SERVER=' + self.config["server"][self.environment] + '; DATABASE=' + self.config["database"] + ';Trusted_Connection=yes;')

        cursor = connection.cursor()

        return(cursor)
    
    def RecordResult(self, testName, message, result):
        """ """
        
        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

        cursor = self.CreateConnection()
        
        SQLCommand = self.config["insertResult"] % (testName, message, result, time)

        try:
            cursor.execute(SQLCommand) # performs query
        except pyodbc.ProgrammingError:
            message = "Error: message format cannot be inserted into database"
            print(" -" + message)
            SQLCommand = self.config["insertResult"] % (testName, message, result, time)
            cursor.execute(SQLCommand)

        cursor.commit()

        return()
    
    def GetLastSessionId(self):
        """ """

        cursor = self.CreateConnection()
        
        SQLCommand = (self.config["get_sessionId"])
        
        cursor.execute(SQLCommand)

        sessionId = int( cursor.fetchone()[0] )

        return( sessionId )


    
    def LogEvent(self, testName, message):
        """ """

        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

        cursor = self.CreateConnection()
        
        SQLCommand = self.config["logEvent"] % (self.sessionId, testName, message, time)
        
        cursor.execute(SQLCommand)

        cursor.commit()        
    
    def GetLastResult(self, testName):
        """ """

        cursor = self.CreateConnection()
        
        SQLCommand = (self.config["get_lastResult"] % testName)

        cursor.execute(SQLCommand)

        try:
            result = cursor.fetchone()[0].strip()
        except TypeError:
            result=None

        return( result )
    
    def GetLastMessage(self, testName):
        """ """

        cursor = self.CreateConnection()
        
        SQLCommand = (self.config["get_lastMessage"] % testName)

        cursor.execute(SQLCommand)

        try:
            message = cursor.fetchone()[0]
        except TypeError:
            message=""

        return( message )
    
    def GetEncryptedPasswords(self):
        """ """
        
        cursor = self.CreateConnection()
        
        SQLCommand = self.config["get_encrypted"]
        
        cursor.execute(SQLCommand)

        return(cursor.fetchall())
    
        
    def GetRecentFailures(self, system):

        cursor = self.CreateConnection()
        
        SQLCommand = (self.config["get_recentFailures"] % system["testName"])

        cursor.execute(SQLCommand)

        results = cursor.fetchone()[0]

        return(results)
    
    def CustomConnection(self, database, authOverride=None):
        """Returns a connection to the db"""

        conxLookup = self.masterConfig["db_connections"][database.lower()]

        if authOverride==None: # Checks for manual override for service account
            if conxLookup["auth"]=="windows":
                connection = pyodbc.connect('DRIVER={' + conxLookup["driver"] + '}; SERVER=' + conxLookup["server"] + '; DATABASE=' + database + ';Trusted_Connection=yes;')
            if conxLookup["auth"]=="azure":
                connection = pyodbc.connect('DRIVER={' + conxLookup["driver"] + '}; SERVER=' + conxLookup["server"] + '; DATABASE=' + database + ';UID=' + self.masterConfig["decrypted"]["idm_username"] + '; PWD=' + self.masterConfig["decrypted"]["idm_password"])
        else:
            username=self.masterConfig["decrypted"][authOverride["username"]]
            password=self.masterConfig["decrypted"][authOverride["password"]]
            connection = pyodbc.connect('DRIVER={' + conxLookup["driver"] + '}; SERVER=' + conxLookup["server"] + '; DATABASE=' + database + ';UID=' + username + '; PWD=' + password)
        
        return(connection)

    
    def RunCustomQuery(self, query, database, authOverride=None):
        
        if authOverride==None:
            connection = self.CustomConnection(database)
        else:
            connection = self.CustomConnection(database, authOverride=authOverride)

        cursor = connection.cursor()

        cursor.execute(query)

        results = cursor.fetchall()

        return(results)

    def Fetchone(self, result):

        return(result[0][0])

        

        