import pytz
import requests
import base64
import json


class JiraClient:
    def __init__(self, 
                 url, 
                 session_endpoint, 
                 issue_endpoint, 
                 username, 
                 password, 
                 api_token, 
                 cookie, 
                 cert, 
                 logger):
        self.logger = logger
        self.url = url
        self.session_endpoint = session_endpoint
        self.issue_endpoint = issue_endpoint
        self.username = username
        self.password = password
        self.api_token = api_token
        self.cert = cert
        self.timezone = pytz.timezone("Europe/Berlin")
        if cookie:
            self.authorization_header_factory = lambda: {"cookie": cookie}
        elif username and password:
            self.authorization_header_factory = self._get_or_create_session_based_authorization_header
        elif username and api_token:
            self.authorization_header_factory = self._create_apitoken_based_authorization_header
        else:
            raise Exception("Cookie or user/password or user/apitoken must be specified")
        
    def allocate_work(self, task_id, date, hours, comment):        
        def allocation_call(authorization_header):
            tz_aware = self.timezone.localize(date)
            dt = tz_aware.strftime('%G-%m-%dT%H:%M:%S.%f')[:-3]
            prepared_date = "%s%s" % (dt, tz_aware.strftime('%z'))
            body = {
                "started": prepared_date,
                "timeSpentSeconds": int(hours * 60 * 60),
                "comment": comment
            }
            response = requests.post(
                f'{self.url}/{self.issue_endpoint}/{task_id.upper()}/worklog', 
                json=body,
                headers=authorization_header, 
                cert=self.cert)
            status_code = response.status_code
            if status_code != 201:
                msg = response
                self.logger.error(f'Error while logging work: {msg}')
                raise JiraClientException(f'Status code: {status_code} \nresponse: \n{msg}')

        self._with_authorization(allocation_call)

    def find_worklog_for_issue(self, task_id):
        def call(authorization_header):
            body = {}
            response = requests.get(f'{self.url}/{self.issue_endpoint}/{task_id}/worklog', json=body,
                                    headers=authorization_header, cert=self.cert)
            return response.json()

        return self._with_authorization(call)

    def _with_authorization(self, func):
        header = self.authorization_header_factory()
        return func(header)

    def _create_apitoken_based_authorization_header(self):
        if not self.api_token:
            raise JiraClientException('API token not specified')
        if not self.username:
            raise JiraClientException('Username not specified')
        credentials = f"{self.username}:{self.api_token}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return {"Authorization": f"Basic {encoded_credentials}",
                "Content-Type": "application/json"}

    def _get_or_create_session_based_authorization_header(self):
        credentials = {"username": self.username, "password": self.password}
        session_response = requests.post(f'{self.url}/{self.session_endpoint}', json=credentials, cert=self.cert)
        if session_response.status_code == 200:
            session_info_json = session_response.json()
            j_session = session_info_json['session']['value']
            self.logger.debug(f'Recieved session (JSESSION={j_session})')
            return {"cookie": f"JSESSIONID={j_session}"}
        else:
            msg = session_response.text
            status_code = session_response.status_code
            self.logger.error(f'Error while receiving session: {msg}')
            raise JiraClientException(f'Status code: {status_code} \nresponse: \n{msg}')


class JiraClientException(Exception):
    def __init__(self, *args):
        super().__init__(*args)
