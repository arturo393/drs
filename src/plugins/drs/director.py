import json
import requests
import sys

from .definitions.nagios import CRITICAL, WARNING
from .dru import DRU


class Director:
    director_api_login = "admin"
    director_api_password = "Admin.123"

    def __init__(self, master_host):
        self.master_host = master_host

    def deploy(self) -> requests.Response:
        director_url = "http://" + self.master_host + "/director/config/deploy"
        director_headers = {
            'Accept': 'application/json',
            'X-HTTP-Method-Override': 'POST'
        }

        try:
            q = requests.post(director_url,
                              headers=director_headers,
                              auth=(self.director_api_login,
                                    self.director_api_password),
                              verify=False,
                              timeout=1)
        except requests.exceptions.RequestException as e:
            print("no connection")
            sys.exit(0)

        return q

    def create_host(self, director_query: dict, update_query: dict) -> requests.Response:

        request_url = "http://" + self.master_host + "/director/host"
        headers = {
            'Accept': 'application/json',
            'X-HTTP-Method-Override': 'POST'
        }

        try:
            q = requests.post(request_url,
                              headers=headers,
                              data=json.dumps(director_query),
                              auth=(self.director_api_login,
                                    self.director_api_password),
                              verify=False,
                              timeout=1)

            hostname = director_query['object_name']
            if q.status_code == 422:
                request_url = "http://" + self.master_host + "/director/host?name=" + hostname
                q = requests.post(request_url,
                                  headers=headers,
                                  data=json.dumps(update_query),
                                  auth=(self.director_api_login,
                                        self.director_api_password),
                                  verify=False,
                                  timeout=1)
            # sys.stderr.write(f"{q.status_code} {q.text}")

        except requests.exceptions.ConnectTimeout as e:
            sys.stderr.write(f"WARNING - {e}")
            sys.exit(WARNING)
        except requests.exceptions.RequestException as e:
            sys.stderr.write(f"CRITICAL - {e}")
            sys.exit(CRITICAL)
        # print(json.dumps(q.json(),indent=2))
        return q

    def modify_service(self, director_query: dict) -> requests.Response:

        request_url = "http://" + self.master_host + "/director/service?name=Status"
        headers = {
            'Accept': 'application/json',
            'X-HTTP-Method-Override': 'POST'
        }

        try:
            q = requests.post(request_url,
                              headers=headers,
                              data=json.dumps(director_query),
                              auth=(self.director_api_login,
                                    self.director_api_password),
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

    def create_dru_host(self, dru: DRU, comm_type: int, type: int, imports, device) -> requests.Response:

        director_query = {
            'object_name': dru.hostname,
            "object_type": "object",
            "address": dru.ip_addr,
            "imports": imports,
            "display_name": dru.name,
            "vars": {
                "opt": str(dru.port),
                "dru": str(dru.position),
                "parents": [dru.parent],
                "device": device,
                "comm_type": str(comm_type),
                "type": str(type)
            }
        }

        request_url = "http://" + self.master_host + "/director/host"
        headers = {
            'Accept': 'application/json',
            'X-HTTP-Method-Override': 'POST'
        }

        try:
            q = requests.post(request_url,
                              headers=headers,
                              data=json.dumps(director_query),
                              auth=(self.director_api_login,
                                    self.director_api_password),
                              verify=False,
                              timeout=1)
            # sys.stderr.write(f"{q.status_code} {q.text}")

            # parent = hostname if connected == 1 else dru_connected[f"opt{opt}"][connected - 2].hostname

            if q.status_code == 422:
                update_query = {
                    "object_type": "object",
                    "address": dru.ip_addr,
                    "imports": imports,
                    "vars": {
                        "opt": str(dru.port),
                        "dru": str(dru.position),
                        "parents": [dru.parent],
                        "device": "dru",
                        "comm_type": str(comm_type)

                    }
                }
                request_url = "http://" + self.master_host + \
                    "/director/host?name=" + dru.hostname
                q = requests.post(request_url,
                                  headers=headers,
                                  data=json.dumps(update_query),
                                  auth=(self.director_api_login,
                                        self.director_api_password),
                                  verify=False,
                                  timeout=1)
                # sys.stderr.write(f"{q.status_code} {q.text}")

        except requests.exceptions.ConnectTimeout as e:
            sys.stderr.write(f"WARNING - {e}")
            sys.exit(WARNING)
        except requests.exceptions.RequestException as e:
            sys.stderr.write(f"CRITICAL - {e}")
            sys.exit(CRITICAL)
        # print(json.dumps(q.json(),indent=2))
        return q

    def get_dru_name(self, dru: DRU) -> requests.Response:

        # Construct query parameters as a string
        query_params = f"name={dru.hostname}"

        request_url = f"http://{self.master_host}/director/host?{query_params}"
        headers = {'Accept': 'application/json'}  # Remove unnecessary header

        try:
            q = requests.get(request_url,
                             headers=headers,
                             auth=(self.director_api_login,
                                   self.director_api_password),
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
