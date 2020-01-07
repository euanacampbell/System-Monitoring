import pyodbc
from datetime import datetime

class Database():

    def __init__(self, config):

        self.config = config
    
    
    def CreateConnection(self):
        connection = pyodbc.connect('DRIVER={' + self.config["driver"] + '}; SERVER=' + self.config["server"] + '; DATABASE=' + self.config["database"] + ';Trusted_Connection=yes;')

        cursor = connection.cursor()

        return(cursor)
    
    def RecordResult(self, testName, message, result):
        """ """

        print("-" + result)
        
        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

        cursor = self.CreateConnection()
        
        SQLCommand = self.config["insertResult"] % (testName, message, result, time)
        cursor.execute(SQLCommand) # performs query 

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

    def IsUserValid(self, user):
        """Return list of valid users in given environemnt"""

        users = getADUsersModule("productionsystemsupport")

        if user in users:
            return(True)
        else:
            return(False)
        
    
    def GetLastResult(self, testName):
        """ """

        cursor = self.CreateConnection()
        
        SQLCommand = (self.config["get_lastResult"] % testName)

        cursor.execute(SQLCommand)

        result = cursor.fetchone()[0].strip()

        return( result )
    
    def GetLastMessage(self, testName):
        """ """

        cursor = self.CreateConnection()
        
        SQLCommand = (self.config["get_lastMessage"] % testName)

        cursor.execute(SQLCommand)

        message = cursor.fetchone()[0]

        return( message )
    
    def GetEncryptedPasswords(self):
        """ """
        
        cursor = self.CreateConnection()
        
        SQLCommand = self.config["get_encrypted"]
        
        cursor.execute(SQLCommand)

        return(cursor.fetchall())
    
        
    def GetRecentFailures(self, system):

        connection = pyodbc.connect('DRIVER={' + self.config["driver"] + '}; SERVER=' + self.config["server"] + '; DATABASE=' + self.config["database"] + ';Trusted_Connection=yes;')

        cursor = connection.cursor()
        
        SQLCommand = (self.config["get_recentFailures"] % system["testName"])

        cursor.execute(SQLCommand)

        results = cursor.fetchone()[0]

        return(results)

    

        