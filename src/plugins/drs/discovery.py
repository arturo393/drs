import json
import socket
import sys
import time

from src.plugins.drs.definitions.nagios import OK, WARNING
from src.plugins.drs.definitions.santone_commands import DRSRemoteSerialCommand
from src.plugins.drs.director import Director
from src.plugins.drs.dru import DRU

fix_ip_end = 0x16
fix_ip_end_opt_1 = 0x64
fix_ip_end_opt_2 = 0x78
fix_ip_end_opt_3 = 0x8C
fix_ip_end_opt_4 = 0xA0

class Discovery:
    """
    Class responsible for discovering and creating DRU devices.
    """

    def __init__(self, baud_rate, dru_connected):

        self.baud_rate = baud_rate
        self.dru_connected = dru_connected

        """
        Initialize the Discovery object with the provided parameters.

        Args:
            parameters (dict): A dictionary containing discovery parameters.
        """

        self.cmd_name_map = {
            1: DRSRemoteSerialCommand.optical_port_device_id_topology_1,
            2: DRSRemoteSerialCommand.optical_port_device_id_topology_2,
            3: DRSRemoteSerialCommand.optical_port_device_id_topology_3,
            4: DRSRemoteSerialCommand.optical_port_device_id_topology_4,
        }


    def _get_director_instance(self):
        """
        Retrieve an instance of the Director class.

        Returns:
            Director: An instance of the Director class.
        """

        _hostname = socket.gethostname()
        _master_host = socket.gethostbyname(_hostname)
        # master_host = '192.168.60.73'
        return Director(_master_host)

    def _create_host_query(self, dru, device, imports, cmd_name=None, baud_rate=19200):
        """
        Generate a query for creating or updating hosts in Icinga 2 Director.

        Args:
            dru (DRU): A DRU object representing the connected DRU device.
            device (str): The type of device to discover (e.g., "dru_ethernet", "dru_serial_host").
            imports (list): A list of imports for the host template.
            cmd_name (str, optional): The command name for serial devices. Defaults to None.

        Returns:
            dict: A query dictionary for creating or updating hosts in Icinga 2 Director.
        """

        query = {
            'object_name': dru.hostname,
            'object_type': 'object',
            'address': dru.ip_addr,
            'imports': imports,
            'display_name': dru.name,
            'vars': {
                'parents': [dru.parent],
                'device': device,
                'baud_rate': str(baud_rate)
            }
        }

        if cmd_name:
            query['vars']['cmd_name'] = cmd_name

        return query

    def _update_service_query(self, dru):
        """
        Generate a query for updating service status in Icinga 2 Director.

        Args:
            dru (DRU): A DRU object representing the connected DRU device.

        Returns:
            dict: A query dictionary for updating service status in Icinga 2 Director.
        """

        return {
            'object_name': 'Status',
            'object_type': 'object',
            'vars': {
                'opt': str(dru.port),
                'dru': str(dru.position),
                'parents': [dru.parent]
            }
        }

    def _log_status(self, dru, message):
        """
        Log status messages to stderr.

        Args:
            dru (DRU): A DRU object representing the connected DRU device.
            message (str): The status message to log.
        """

        sys.stderr.write(f"{dru} {message} \n")

    def _deploy_if_needed(self, director, response):
        """
        Deploy changes to Icinga 2 Director if the response status code indicates a need to deploy.

        Args:
            director (Director): An instance of the Director class.
            response (requests.Response): The response from the API call.
        """

        if response.status_code != 304:
            director.deploy()

    def _process_response(self, dru, message, response, director):
        """
        Process and log the response from Icinga 2 Director, and deploy changes if necessary.

        Args:
            dru (DRU): A DRU object representing the connected DRU device.
            message (str): The status message to log.
            response (requests.Response): The response from the API call.
            director (Director): An instance of the Director class.
        """
        if response.status_code != 304:
            # self._log_status(dru, message)
            self._deploy_if_needed(director, response)


    def discover_remotes(self, parameters):
        """
        Handle device discovery for the specified device type.

        This method performs the discovery process for DRU Ethernet devices.
        It identifies connected DRU devices, creates the necessary host objects
        in Icinga 2 Director, and updates the parameters dictionary with
        the execution time.
        """
        start_time = time.time()
        director = self._get_director_instance()

        device_config = {
            "type": "dru_ethernet",
            "imports": ["ethernet-host-template"],
            "baud_rate": self.baud_rate
        }

        for opt, dru_list in self.dru_connected.items():
            for dru in dru_list:
                self._process_dru(director, dru, device_config)

        parameters["dt"] = str(time.time() - start_time)

        return OK

    def _process_dru(self, director, dru, device_config):
        """
        Process a single DRU device.

        Args:
            director: The Director instance.
            dru: The DRU object to process.
            device_config (dict): Configuration for the device.
        """
        cmd_name = self.cmd_name_map.get(dru.port)
        dru.name = self._get_dru_name(director, dru)

        director_query = self._create_host_query(dru, device_config["type"], device_config["imports"], cmd_name,
                                                 device_config["baud_rate"])
        update_query = self._create_host_query(dru, device_config["type"], device_config["imports"], cmd_name,
                                               device_config["baud_rate"])

        response = director.create_host(director_query=director_query, update_query=update_query)
        message = "Create -> Success" if response.status_code == 200 else f"Create -> {response.text}"

        self._process_response(dru, message, response, director)
        if response.status_code == 200:
            self._modify_service_status()

    def _get_dru_name(self, director, dru):
        """
        Get the DRU name from the director.

        Args:
            director: The Director instance.
            dru: The DRU object.

        Returns:
            str: The DRU name.
        """
        response = director.get_dru_name(dru)
        if response.status_code == 200:
            data = json.loads(response.text)
            return data.get('display_name', dru.name)
        return dru.name

    def _modify_service_status(self):
        """
        Modify service status for devices discovered using serial discovery.

        Iterates through the connected DRU devices and constructs a query for updating
        the service status for each device. Sends the query to Icinga 2 Director and
        processes the response, logging status messages and deploying changes if necessary.
        """

        director = self._get_director_instance()
        dru_connected = self._dru_connected_search()

        for opt in dru_connected:
            for dru in dru_connected[opt]:
                director_query = self._update_service_query(dru)
                response = director.modify_service(director_query=director_query)

                message = (
                    f"Success - Service modified"
                    if response.status_code == 200
                    else f"Error - {response.text}"
                )

                self._process_response(dru, message, response, director)

