from src.plugins.drs.alarm import Alarm
from src.plugins.drs.definitions import OK, WARNING, CRITICAL
from src.plugins.drs.graphite import Graphite
from src.plugins.drs.html_table import HtmlTable

class PluginOutput:
    def __init__(self, parameters):
        self.parameters = parameters
        # Define a dictionary of command types and corresponding functions
        self.command_functions = {
            'dru_serial_service': self.dru_serial_display,
            'dru_serial_host': self.dru_serial_host_display,
            'dmu_serial_service': self.get_master_remote_service_message,
            'dmu_serial_host': self.dmu_serial_host_display,
            'dru_ethernet': self.get_master_remote_service_message,
            'dmu_ethernet': self.get_master_remote_service_message,
            'discovery_ethernet': self.discovery_display,
            'discovery_serial': self.discovery_display,
            'discovery_redboard_serial': self.discovery_display
        }

    def dru_serial_display(self):
        graphite = ""
        alarm = Alarm(self.parameters)
        exit_code = alarm.check_alarm()
        html_table = HtmlTable(self.parameters, alarm)
        graphite = Graphite(self.parameters)
        plugin_output_message = (html_table.ltel_board_table() + "|" + graphite.display())
        return exit_code, plugin_output_message

    def dru_serial_host_display(self):
        rt = self.parameters['rt']
        device_id = int(self.parameters["hostname"][3:])
        optical_port = self.parameters["optical_port"]
        if optical_port is None:
            exit_value = CRITICAL
            message = f"CRITICAL - No optical_port defined in service"
            return exit_value, message
        key_name = f"optical_port_device_id_topology_{optical_port}"
        optical_port_device_id_topology = self.parameters.get(key_name, None)
        exit_value = CRITICAL
        message = f"CRITICAL - No id {device_id} found"
        if optical_port_device_id_topology is not None:
            for key, value in optical_port_device_id_topology.items():
                if value == device_id:
                    message = f"OK - id {device_id} found"
                    exit_value = OK
        graphite = Graphite(self.parameters)
        rt = round(float(rt), 2)
        plugin_output_message = f"{message}, RTA = {rt} ms | {graphite.dmu_serial_single()}"
        exit_code = exit_value
        return exit_code, plugin_output_message

    def dmu_serial_host_display(self):
        rt = self.parameters['rt']

        graphite = Graphite(self.parameters)
        rt = round(float(rt), 2)
        plugin_output_message = f"OK - RTA = {rt} ms | {graphite.display()}"
        exit_code = OK
        return exit_code, plugin_output_message

    def get_master_remote_service_message(self):

        graphite = ""
        alarm = Alarm(self.parameters)

        html_table = HtmlTable(self.parameters, alarm)
        graphite = Graphite(self.parameters)
        plugin_output_message = f"{html_table.display()}|{graphite.display()}"
        exit_code = alarm.check_exit_code()
        if self.parameters['cmd_type'] == 'single_set':
            plugin_output_message = "OK"
        return exit_code, plugin_output_message

    def discovery_display(self):
        rt = self.parameters['rt']
        dt = self.parameters['dt']
        alarm = Alarm(self.parameters)
        html_table = HtmlTable(self.parameters, alarm)
        graphite = Graphite(self.parameters)
        rt = round(float(rt), 2)
        dt = round(float(dt), 2)
        plugin_output_message = f"{html_table.discovery_table()}|{graphite.display()}"
        exit_code = OK
        return exit_code, plugin_output_message

    def create_message(self):
        device = self.parameters['device']
        if device in self.command_functions:
            get_message = self.command_functions.get(device)
            exit_code, message = get_message()
            return exit_code, message
        else:
            return WARNING, f"WARNING  - no output message for {device}"
