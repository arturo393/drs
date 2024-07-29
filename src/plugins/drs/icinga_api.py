import json
import requests
import sys

from src.plugins.drs.definitions.nagios import CRITICAL, WARNING

class IcingaApi:
    icinga_api_login = "root"
    icinga_api_password = "Admin.123"

    def __init__(self, master_host):
        self.master_host = master_host

    def _modify_hostname_service(self, hostname, servicename, icinga_query: dict):

        request_url = f"https://{self.master_host}:5665/v1/objects/hosts/{hostname}"
        headers = {
            'Accept': 'application/json',
            'X-HTTP-Method-Override': 'POST'
        }

        try:
            q = requests.post(request_url,
                              headers=headers,
                              data=json.dumps(icinga_query),
                              auth=(self.icinga_api_login, self.icinga_api_password),
                              verify=False,
                              timeout=1)

        except requests.exceptions.ConnectTimeout as e:
            sys.stderr.write(f"WARNING - {e}")
            sys.exit(WARNING)
        except requests.exceptions.RequestException as e:
            sys.stderr.write(f"CRITICAL - {e}")
            sys.exit(CRITICAL)
        # print(json.dumps(q.json(),indent=2))
        return q

    def _log_status(self, message):
        """
        Log status messages to stderr.

        Args:
            message (str): The status message to log.
        """

        sys.stderr.write(f"{message} \n")

    def _process_dmu_response(self, message, response):
        """
        Process and log the response from Icinga 2 Director, and deploy changes if necessary.

        Args:
            message (str): The status message to log.
            response (requests.Response): The response from the API call.
        """
        if response.status_code != 304:
            self._log_status(message)
