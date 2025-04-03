#!/bin/bash

USERNAME=''
TOKEN=''
URL=''

curl -u $USERNAME:$TOKEN -X GET $URL/rest/api/2/serverInfo
