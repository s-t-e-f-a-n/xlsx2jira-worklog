#!/bin/bash

USERNAME=""
TOKEN=""
URL=""

# Example of a POST request to add a worklog
curl -u "$USERNAME:$TOKEN" -X POST -H "Content-Type: application/json" \
     -d '{"comment": "Worked on the feature implementation.","started": "2025-03-29T10:00:00.000+0000","timeSpentSeconds": 3600}' \
     "$URL/rest/api/2/issue/ORG-12/worklog"

# Example of a DELETE request to remove a worklog
curl --request DELETE \
  --url "$URL/rest/api/2/issue/234455/worklog/286233" \
  --user "$USERNAME:$TOKEN" \
  --header 'Content-Type: application/json'
