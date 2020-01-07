from jira import JIRA
import re

class JiraController():

    def __init__(self,username,password):

        
        self.server = ""
        self.jira = JIRA(basic_auth=(username,password), options={'server':self.server})
    
      

    def RaiseTicket(self, system, message):
        print("Raising Jira ticket")

        issue_dict = {
                    'project' : {'id': 10001},
                    'summary': 'Alert: ' + system,
                    'description' : message,
                    'issuetype' : {'name' : 'Incident'},
                    "customfield_12200" :  [{"key" : "SC-40"}]
                    } 
            
        new_issue = self.jira.create_issue(fields=issue_dict)
        return(new_issue)




