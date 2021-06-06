from jira import JIRA
import re

class JiraController():

    def __init__(self,username,password):

        
        self.server = "URL"
        self.jira = JIRA(basic_auth=(username,password), options={'server':self.server})
    
      

    def RaiseTicket(self, system, message):
        issue_dict = {
                    'field':'value'
                    } 
            
        new_issue = self.jira.create_issue(fields=issue_dict)
        return(new_issue)




