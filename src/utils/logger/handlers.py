import os
import requests
import json
from logging import Handler, Formatter, NOTSET

class SlackHandler(Handler):
    def __init__(self, level=NOTSET, slack_url=None):
        super().__init__()
        if slack_url is None:
            self.slack_url = os.environ["ASGARD_SLACK_URL"]
        else:
            self.slack_url = slack_url
    def emit(self, record):
        formatted_log = self.format(record)
        requests.post(
            self.slack_url, 
            json.dumps({"text": formatted_log }), 
            headers={"Content-Type": "application/json"})