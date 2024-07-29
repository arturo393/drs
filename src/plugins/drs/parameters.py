from src.plugins.drs.dru import DRU


class Parameters:
    """
     Class responsible for discovering and creating DRU devices.
    """

    def __init__(self, parameters):

        self.parameters = parameters
        self.net_prefix = parameters["device_id"]
        self.hostname = parameters["hostname"]

    def get_connected_dru(self) -> dict:
        """
        Identify and gather information about connected DRU devices.

        This method iterates through the configured optical ports and retrieves
        information about the connected DRU devices. It constructs a dictionary
        storing the discovered DRU devices and their corresponding information.

        Args:
            parameters (dict): A dictionary containing the necessary parameters.

        Returns:
            dict: A dictionary containing discovered DRU devices and their information.
        """
        dru_connected = {}

        for optical_port in range(1, 5):
            port_name = f"optical_port_devices_connected_{optical_port}"
            devices_connected = self.parameters[port_name]
            if devices_connected == "-":
                continue

            dru_connected[f"opt{optical_port}"] = []
            for connected in range(1, int(devices_connected) + 1):
                device_id = self._get_device_id(self.parameters, optical_port, connected)
                if device_id == 0:
                    continue

                ip = self._generate_ip(self.net_prefix, optical_port, connected)
                parent = self._get_parent_name(self.hostname, dru_connected, optical_port, connected)

                dru = DRU(connected, optical_port, device_id, self.hostname, ip, parent)
                dru_connected[f"opt{optical_port}"].append(dru)

                self._update_parameters_with_ip(self.parameters, optical_port, connected, ip)

        return dru_connected

    def _get_device_id(self, parameters, opt, connected):
        id_key = f"optical_port_device_id_topology_{opt}"
        return parameters.get(id_key, {}).get(f"id_{connected}", 0)

    def _generate_ip(self, net, opt, connected):
        fix_ip_start = 0xC0
        fix_ip_end_opt = [0, 100, 120, 140, 160]
        return f"{fix_ip_start}.{net}.{fix_ip_end_opt[opt] + connected - 1}"

    def _update_parameters_with_ip(self, parameters, opt, connected, ip):
        connected_ip_addr_name = f"optical_port_connected_ip_addr_{opt}{connected}"
        parameters[connected_ip_addr_name] = ip

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
