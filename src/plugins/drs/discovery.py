import json
import socket
import sys
import time

from src.plugins.drs.definitions import OK, WARNING
from src.plugins.drs.definitions import DRSRemoteSerialCommand
from src.plugins.drs.director import Director
from src.plugins.drs.dru import DRU

class Discovery:
    """
    Class responsible for discovering and creating DRU devices.
    """

    def __init__(self, parameters):
        """
        Initialize the Discovery object with the provided parameters.

        Args:
            parameters (dict): A dictionary containing discovery parameters.
        """

        self.parameters = parameters

        self.cmd_name_map = {
            1: DRSRemoteSerialCommand.optical_port_device_id_topology_1,
            2: DRSRemoteSerialCommand.optical_port_device_id_topology_2,
            3: DRSRemoteSerialCommand.optical_port_device_id_topology_3,
            4: DRSRemoteSerialCommand.optical_port_device_id_topology_4,
        }

    def search_and_create_dru(self):
        """Discover DRU based on device type."""

        device = self.parameters["device"]

        if device == "discovery_ethernet":
            self._discover_ethernet()
        elif device == "discovery_serial":
            self._discover_serial()
        elif device == "discovery_redboard_serial":
            self._discover_redboad_serial()
        else:
            return WARNING
        return OK

    def _get_director_instance(self):
        """
        Retrieve an instance of the Director class.

        Returns:
            Director: An instance of the Director class.
        """

        hostname = socket.gethostname()
        master_host = socket.gethostbyname(hostname)
        # master_host = '192.168.60.73'
        return Director(master_host)

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

    def _dru_connected_search(self):
        """
        Identify and gather information about connected DRU devices.

        This method iterates through the configured optical ports and retrieves
        information about the connected DRU devices. It constructs a dictionary
        storing the discovered DRU devices and their corresponding information.

        Returns:
            dict: A dictionary containing discovered DRU devices and their information.
        """

        hostname = self.parameters["hostname"]
        dru_connected = {}

        for opt in range(1, 5):
            port_name = f"optical_port_devices_connected_{opt}"
            optical_port_devices_connected = 0 if self.parameters[port_name] == "-" else self.parameters[port_name] + 1

            dru_connected[f"opt{opt}"] = []
            for connected in range(1, optical_port_devices_connected):
                fix_ip_start = 0xC0
                fix_ip_end_opt = [0, 100, 120, 140, 160]
                net = self.parameters["device_id"]
                id_key = f"optical_port_device_id_topology_{opt}"
                # device_id = self.parameters[id_key][f"id_{connected}"]
                device_id = self.parameters.get(id_key, {}).get(f"id_{connected}")
                parent = self._get_parent_name(hostname, dru_connected, opt, connected)
                ip = f"{fix_ip_start}.{net}.{fix_ip_end_opt[opt] + connected - 1}"

                if device_id == 0:
                    pass
                else:
                    d = DRU(connected, opt, device_id, hostname, ip, parent)
                    dru_connected[f"opt{opt}"].append(d)
                    connected_ip_addr_name = f"optical_port_connected_ip_addr_{opt}{connected}"
                    self.parameters[connected_ip_addr_name] = ip

        return dru_connected

    def _get_dru_connected_number(self):
        """
        Identify and gather information about connected DRU devices.

        This method iterates through the configured optical ports and retrieves
        information about the connected DRU devices. It constructs a dictionary
        storing the discovered DRU devices and their corresponding information.

        Returns:
            dict: A dictionary containing discovered DRU devices and their information.
        """
        # Get the hostname from the parameters
        hostname = self.parameters["hostname"]

        # Create an empty dictionary to store the connected DRU devices
        dru_connected = {}

        # Iterate through the optical ports
        for opt in range(1, 5):
            # Get the parameter name for the current optical port
            port_name = f"optical_port_devices_connected_{opt}"

            # Get the value of the parameter
            optical_port_devices_connected = 0 if self.parameters[port_name] == "-" else self.parameters[port_name]

            # Add the connected DRU device to the dictionary
            dru_connected[f"opt{opt}"] = optical_port_devices_connected

        # Return the dictionary containing the discovered DRU devices
        return dru_connected

    def _get_parent_name(self, hostname, dru_connected, opt, connected):
        """
        Gets the name of the parent according to the given conditions.

        Args:
            hostname (str): The name of the current host.
            dru_connected (dict): A dictionary containing information about the DRU connection.
            opt (int): The option to consider.
            connected (int): The connection status.

        Returns:
            str: The name of the parent or None if not found.

        """
        try:
            parent = hostname if connected == 1 else dru_connected[f"opt{opt}"][connected - 2].hostname
        except KeyError:
            # print("Key not found in dru_connected dictionary")
            parent = None
        except IndexError:
            # print("Index out of range in dru_connected list")
            parent = None
        except AttributeError:
            # print("Attribute error accessing .hostname")
            parent = None
        return parent

    def _discover_device(self, device, imports, cmd_name=None):
        """
        Handle device discovery for the specified device type.

        This method performs the discovery process for the given device type.
        It identifies connected DRU devices, creates the necessary host objects
        in Icinga 2 Director, and updates the parameters dictionary with
        the execution time.

        Args:
            device (str): The type of device to discover (e.g., "dru_ethernet", "dru_serial_host").
            imports (list): A list of imports for the host template.
            cmd_name (str, optional): The command name for serial devices. Defaults to None.
        """

        dt = time.time()
        director = self._get_director_instance()
        dru_connected = self._dru_connected_search()
        baud_rate = self.parameters['baud_rate']

        for opt in dru_connected:

            for dru in dru_connected[opt]:
                if dru.port in self.cmd_name_map:
                    cmd_name = self.cmd_name_map[dru.port]
                response = director.get_dru_name(dru)
                if response.status_code == 200:
                    text = response.text
                    data = json.loads(text)
                    dru.name = data.get('display_name', dru.name)

                director_query = self._create_host_query(dru, device, imports, cmd_name, baud_rate)
                update_query = self._create_host_query(dru, device, imports, cmd_name, baud_rate)

                response = director.create_host(director_query=director_query, update_query=update_query)
                message = "Create -> Success" if response.status_code == 200 else "Create -> " + str(response.text)

                self._process_response(dru, message, response, director)
                if response.status_code == 200:
                    self._modify_service_status()

        self.parameters["dt"] = str(time.time() - dt)

    def _discover_ethernet(self):
        """
        Perform discovery and creation for Ethernet DRU devices.

        This method handles the discovery process for Ethernet-based DRU devices.
        It creates the necessary host objects in Icinga 2 Director and deploys the changes.

        """

        device = "dru_ethernet"
        imports = ["ethernet-host-template"]
        self._discover_device(device, imports)

    def _discover_serial(self):
        """
        Perform discovery and creation for Serial DRU devices.

        This method handles the discovery process for Serial-based DRU devices.
        It creates the necessary host objects in Icinga 2 Director and deploys the changes.
        Additionally, it updates the service status for the discovered devices.

        """

        device = "dru_serial_host"
        imports = ["serial-host-template"]
        cmd_name = "254"
        self._discover_device(device, imports, cmd_name)

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
