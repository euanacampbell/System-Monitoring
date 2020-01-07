import requests
import json

class Comms():

    def __init__(self, config, slackStatus):

        self.url = config
        self.slackStatus = slackStatus

    
    def PostToSlack(self, testName, message):
        """ """
        print("-Printing to Slack")

        message = "*" + testName + ":* " + message

        if self.slackStatus == "on":
            webhook_url = self.url
            
            slack_data = {'text': message}
            response = requests.post(
                webhook_url, data=json.dumps(slack_data),
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code != 200:
                raise ValueError(
                    'Request to slack returned an error %s, the response is:\n%s'
                    % (response.status_code, response.text)
                )