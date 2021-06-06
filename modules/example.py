class example():

    def __init__(self, config):
        """Controls processes"""

        self.config = config["test"]


        self.response = {
            "result": "passed",
            "message": "blank message"
        }
        
    def __run__(self):
        """Controls process flow for test, returns the results"""

        # Call your other functions here
        self.OtherFunctions()


        return( self.response ) 


    def OtherFunctions(self):
        """  """

        # Test something here and modify self.response

        pass