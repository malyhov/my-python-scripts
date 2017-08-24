#!/usr/bin/env python3

import requests
import sys


ISSUE_NAME = sys.argv[1]
URL_JIRA_ISSUE = "http://jira/rest/api/latest/issue"
HEADERS = {
    'authorization': "Basic Secret-String",
    'content-type': "application/json"    
    }

url = URL_JIRA_ISSUE + "/{}/transitions".format(ISSUE_NAME)
querystring = {"expand":"transitions.fields"}
payload = "{ \"update\": { \"comment\": [ { \"add\": {\"body\": \"Таск переоткрыт.\"} }]},\"transition\": {\"id\": \"3\"}}"
response = requests.request("POST", url, data=payload, headers=HEADERS, params=querystring)
print("----- Issue Name: %s" % ISSUE_NAME)
print(response.text)
print("-------------------------------------------------------------")
