import requests
import json

# jira credentials
jira_url = "" # the base url of your jira instance
api_token = ""  # your api token
username = ""  # your email login

# test jira issue key
url = f"{jira_url}/rest/api/2/issue/ORG-12/worklog"

# test worklog payload
payload = {
    "comment": "Test",
    "started": "2025-03-29T10:00:00.000+0000",
    "timeSpentSeconds": 3600
}

# HTTP Header
headers = {
    "Content-Type": "application/json"
}

print ("URL: ", url)
print ("Headers: ", headers)
print ("Username: ", username)
print ("Payload: ", json.dumps(payload))

# POST request to Jira API
response = requests.post(
    url,
    headers=headers,
    auth=(username, api_token),
    data=json.dumps(payload)
)

# check response
if response.status_code == 201:
    print("Worklog successfully logged!")
else:
    print(f"Error at logging: {response.status_code}, {response.text}")