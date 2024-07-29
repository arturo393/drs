import sys

from src.plugins.drs.alarm import Alarm
from src.plugins.drs.definitions.nagios import CRITICAL, WARNING, UNKNOWN

class HtmlTable:

    def __init__(self, parameters, alarm: Alarm):
        self.parameters = parameters
        self.alarm = alarm
        # Default color and font size for normal conditions
        self.default_font_color = "#10263b"
        self.default_background_color = "white"
        self.default_font_size = "font-size:12px"

        # Alarm color and font size for critical and warning conditions
        self.critical_color = "#ff5566"
        self.alarm_font_color = "white"
        self.warning_color = "#ffaa44"
        self.alarm_font_size = "font-size:14px"

    def display(self):
        # device_table = dmu_table(parameters) if device == 'dmu' else dru_table(parameters)
        device_table = self.if_board_table()
        channel_table = self._get_channel_freq_table()
        table = ""
        table += '<div class="sigma-container">'
        table += device_table + channel_table
        table += "</div>"
        return table

    def discovery_table(self):
        table = ""
        table += '<div class="sigma-container">'
        table += self.get_opt_connected_table()
        table += "</div>"
        return table

    def dru_table(self):
        power_att_table = self.get_power_table()
        vswr_temperature_table = self.get_vswr_temperature_table()
        return power_att_table + vswr_temperature_table

    def dmu_table(self):
        opt_status_table = self.get_opt_status_table()
        power_table = self.get_power_table()
        return opt_status_table + power_table

    def ltel_board_table(self):

        table = ""
        table += '<div class="sigma-container">'
        table += self.get_power_table()
        table += self.get_vswr_temperature_table()
        table += self._get_ltel_board_channel_freq_table()
        table += "</div>"
        return table

    def if_board_table(self):
        table = ""
        table += self.get_opt_status_table()
        table += self.get_power_table()
        table += self.get_vswr_temperature_table()
        return table

    def _get_ltel_board_channel_freq_table(self):

        channel_bandwidth = self.parameters.get('channel_bandwidth', 0)
        uplink_start_frequency = self.parameters.get('uplink_start_frequency', 0)
        for channel in range(1, 17):
            channel_key = f"channel_{channel}"
            ul_ch_freq = uplink_start_frequency + self.parameters.get(f"{channel_key}_number", 0) * channel_bandwidth
            self.parameters[f"{channel_key}_freq"] = round(ul_ch_freq, 3)
        return self._get_channel_freq_table()

    def _get_channel_freq_table(self):
        """
        Generates HTML table with frequency and status data based on the working mode.

        Returns:
            table_html (str): HTML formatted string of the data table.

        If KeyError occurs during the operation, it prints an error message
        to stderr and exits with an UNKNOWN status. If a key is not found in self.parameters,
        it sets the respective parameter value to '-'.
        """
        # Initialize empty lists
        frequencies = []
        status = []

        try:
            # Fetch parameters with '.get()' and default to '-' if key not found
            working_mode = self.parameters.get('working_mode', '-')
            work_bandwidth = self.parameters.get("work_bandwidth", 0)
            uplink_start_frequency = self.parameters.get('uplink_start_frequency', 0)
            work_bandwidth = self.parameters.get('work_bandwidth', 0)
            central_frequency_point = self.parameters.get('central_frequency_point', 0)

            if central_frequency_point == 0:
                if uplink_start_frequency == 0 and work_bandwidth == 0:
                    central_frequency_point = 0
                else:
                    central_frequency_point = uplink_start_frequency + (work_bandwidth / 2.0)

                # Construct frequency and status lists
            for channel in range(1, 17):
                frequencies.append(self.parameters.get(f"channel_{channel}_freq", '-'))
                status.append(self.parameters.get(f"channel_{channel}_status", '-'))

        except Exception as e:
            sys.stderr.write(f"UNKNOWN - Error: {str(e)}")
            sys.exit(UNKNOWN)

        table_html = ""

        # Construct HTML table according to working mode
        if working_mode == 'Channel Mode':
            table_html += self._generate_channel_mode_table(frequencies, status)
        else:
            table_html += self._generate_other_mode_table(working_mode, work_bandwidth, central_frequency_point)

        return table_html

    def _generate_channel_mode_table(self, frequencies: list, status: list) -> str:
        """
        Generates HTML table for the 'Channel Mode'.

        Arguments:
            frequencies (list): List of frequency data.
            status  (list): List of status data.

        Returns:
            str: HTML formatted string of the data table.
        """

        if self.parameters['device'] == 'dmu_ethernet':
            frequency = "Downlink"
        else:
            frequency = "Uplink"

        table_html = f"<table width=100%>" \
                     f"<thead><tr style=font-size:11px>" \
                     f"<th width='5%'>Channel</font></th>" \
                     f"<th width='5%'>Status</font></th>" \
                     f"<th width='50%'>{frequency} [Mhz]</font></th>" \
                     f"</tr></thead><tbody>"

        for i in range(16):
            table_html += f"<tr align='center' style=font-size:12px>" + \
                          f"<td>{i + 1}</td>" + \
                          f"<td>{status[i]}</td>" + \
                          f"<td>{frequencies[i]}</td>" + \
                          "</tr>"

        return table_html + "</tbody></table>"

    def _generate_other_mode_table(self, working_mode: str,
                                   work_bandwidth: int,
                                   central_frequency_point: int) -> str:
        """
        Generates HTML table for working modes other than 'Channel Mode'.

        Arguments:
            working_mode (str): The working mode of the system.
            work_bandwidth (int): Work bandwidth data.
            central_frequency_point (int): Central frequency point data.

        Returns:
            str: HTML formatted string of the data table.
        """
        table_html = "<table width=90%>" + \
                     "<thead><tr style=font-size:12px>" + \
                     "<th width='10%'>Mode</font></th>" + \
                     "<th width='30%'>Work Bandwidth [Mhz]</font></th>" + \
                     "<th width='30%'>Central Frequency Point [Mhz]</font></th>" + \
                     "</tr></thead><tbody>" + \
                     "<tr align='center' style=font-size:12px>" + \
                     f"<td>{working_mode}</td>" + \
                     f"<td>{work_bandwidth}</td>" + \
                     f"<td>{central_frequency_point}</td>" + \
                     "</tr></tbody></table>"

        return table_html

    def get_power_table(self):
        """
        Generates an HTML table displaying power and attenuation information.
        Applies styling based on alarm conditions.

        Returns:
            str: The generated HTML table. In case of an error, an empty string is returned.
        """
        try:
            # retrieve and initialize styles
            default_style = f"style=font-size:12px"
            uplink_power_style = default_style
            downlink_power_style = default_style

            # Update uplink and downlink_power_style based on alarm statuses
            # _get_alarm_style is extrapolated to be a part of this class and hence we use self
            if self.alarm.uplink_power_alarm == CRITICAL:
                uplink_power_style = self._get_alarm_style(self.critical_color, self.alarm_font_size)
            elif self.alarm.uplink_power_alarm == WARNING:
                uplink_power_style = self._get_alarm_style(self.warning_color, self.alarm_font_size)

            if self.alarm.downlink_power_alarm == CRITICAL:
                downlink_power_style = self._get_alarm_style(self.critical_color, self.alarm_font_size)
            elif self.alarm.downlink_power_alarm == WARNING:
                downlink_power_style = self._get_alarm_style(self.warning_color, self.alarm_font_size)

            device = self.parameters.get('device', "")
            if device == "dmu_ethernet":
                uplink_attenuation_power = self.parameters.get('upAtt', "")
                downlink_attenuation_power = self.parameters.get('dlAtt', "")
                downlink_input_power = self.parameters.get('uplink_input_power', "")
                uplink_output_power = self.parameters.get('downlink_output_power', "")
                table = ("<table width=250>"
                     "<thead>"
                     "<tr align=\"center\" style=font-size:12px>"
                     "<th width='12%'>Link</font></th>"
                     "<th width='12%'>Direction</font></th>"
                     "<th width='33%'>Power</font></th>"
                     "<th width='10%'>Attenuation</font></th>"
                    "<th width='12%'>Direction</font></th>"
                    "<th width='12%'>Power</font></th>"
                     "</tr></thead>"
                     "<tbody>"
                     f"<tr align=\"center\" {uplink_power_style}><td>Uplink</td>"
                     f"<td>Output</td>"
                     f"<td>{uplink_output_power}[dBm]</td>"
                     f"<td>{uplink_attenuation_power}[dB]</td>"
                     f"<td>Input</td>"
                     f"<td>{round(uplink_output_power-uplink_attenuation_power,2)}[dBm]</td></tr>"
                     f"<tr align=\"center\"{downlink_power_style}><td>Downlink</td>"
                     f"<td>Input</td>"
                     f"<td>{downlink_input_power}[dBm]</td>"
                     f"<td>{downlink_attenuation_power}[dB]</td>"
                     f"<td>Output</td>"
                     f"<td>{round(downlink_input_power - downlink_attenuation_power,2)}[dBm]</td></tr>"
                     "</tbody></table>")
                return table
            else:
                uplink_attenuation_power = self.parameters.get('dlAtt', "")
                downlink_attenuation_power = self.parameters.get('upAtt', "")
                uplink_input_power = self.parameters.get('uplink_input_power', "")
                downlink_output_power = self.parameters.get('downlink_output_power', "")
            # Generate HTML structure according to given format
                table = ("<table width=250>"
                        "<thead>"
                        "<tr align=\"center\" style=font-size:12px>"
                        "<th width='12%'>Link</font></th>"
                        "<th width='12%'>Direction</font></th>"
                        "<th width='33%'>Power</font></th>"
                        "<th width='10%'>Attenuation</font></th>"
                        "<th width='12%'>Direction</font></th>"
                        "</tr></thead>"
                        "<tbody>"
                        f"<tr align=\"center\" {uplink_power_style}><td>Uplink</td>"
                        f"<td>Input</td>"
                        f"<td>{uplink_input_power}[dBm]</td>"
                        f"<td>{uplink_attenuation_power}[dB]</td></tr>"
                        f"<tr align=\"center\"{downlink_power_style}><td>Downlink</td>"
                        f"<td>Output</td>"
                        f"<td>{downlink_output_power}[dBm]</td>"
                        f"<td>{downlink_attenuation_power}[dB]</td></tr>"
                        "</tbody></table>")
                return table

        except (KeyError, AttributeError) as e:
            # Write error to stderr and exit with status UNKNOWN when there is an Exception
            sys.stderr.write(f"UNKNOWN - Error: {str(e)}")
            sys.exit(UNKNOWN)

    def _get_alarm_style(self, color, font_size):
        """
        Defines the HTML style string for alarms.

        Args:
            color (str): The color for the alarm string.
            font_size (str): The font size for the alarm string.

        Returns:
            str: The HTML style string.
        """
        return f"style=font-size:{font_size};color:{color}"

    def get_vswr_temperature_table(self):
        # Define default styling
        default_style = f"style=font-size:12px"
        temperature_style = default_style

        # Update styling based on alarm conditions
        if self.alarm.temperature_alarm is CRITICAL:
            temperature_style = self._get_alarm_style(self.critical_color, self.alarm_font_size)
        elif self.alarm.temperature_alarm is WARNING:
            temperature_style = self._get_alarm_style(self.warning_color, self.alarm_font_size)

        if 'temperature' in self.parameters:
            temperature = self.parameters.get('temperature', "")
        elif 'power_amplifier_temperature' in self.parameters:
            temperature = self.parameters.get('power_amplifier_temperature', "")
        else:
            temperature = ""

        # Define table header with styling
        table2 = \
            "<table width=10%>" \
            "<thead>" \
            "<tr  style=font-size:12px>" \
            "<th width='40%'>Temperature</font></th>" \
            "</tr>" \
            "</thead>"
        # Populate table body with power and attenuation values
        table2 += \
            "<tbody>" \
            f"<tr align=\"center\" {temperature_style}>" \
            f"<td>{temperature} [&deg;C] </td> " \
            "</tr>" \
            "</tbody></table>"
        return table2

    def _get_alarm_style(self, color, font_size):
        """
        Generates an inline CSS style string based on the provided color and font size.

        Args:
            color (str): The background color for alarm indication.
            font_size (str): The font size for alarm indication.

        Returns:
            str: The generated inline CSS style string
        """

        background_color = f"background-color:{color}"
        font_color = f"color:white"
        return f"style={background_color};{font_color};{font_size}"

    def get_opt_status_table(self):
        """
        Generates an HTML table displaying optical port status information.
        Determines the number of ports based on the device type.

        Returns:
            str: The generated HTML table.
        """
        try:
            # Attempt to fetch device parameter
            device = self.parameters["device"]

            # Determine the range for optical ports based on device type
            opt_range = self._get_opt_range(device)

            # Initiate HTML table string
            table = "<table width=280>"

            # Define HTML table header
            table += ("<thead><tr align=\"center\" style=font-size:12px>"
                      "<th width='12%'>Port</font></th>"
                      "<th width='22%'>Activation Status</font></th>"
                      "<th width='22%'>Connected Devices</font></th>"
                      "<th width='20%'>Transmission Status</font></th>"
                      "</tr></thead>")

            # Start HTML table body
            table += "<tbody>"

            for i in range(1, opt_range + 1):
                # Construct parameter keys for connected devices and transmission status
                connected_key = f"optical_port_devices_connected_{i}"
                transmission_status_key = f"opt_{i}_transmission_status"
                activation_status_key = f"opt_{i}_activation_status"
                # Try to fetch connected devices and transmission status from parameters
                connected = str(self.parameters.get(connected_key, ""))
                transmission_status = str(self.parameters.get(transmission_status_key, ""))
                activation_status = str(self.parameters.get(activation_status_key, ""))

                # Construct HTML table row with necessary information
                table += ("<tr align=\"center\" style=font-size:12px>"
                          f"<td>opt{i}</td>"
                          f"<td>{activation_status}</td>"
                          f"<td>{connected}</td>"
                          f"<td>{transmission_status}</td>"
                          "</tr>")

            # Close HTML table body and table
            table += "</tbody></table>"

            return table

        except (KeyError, TypeError) as e:
            # Print error message to stderr and exit with status UNKNOWN
            sys.stderr.write(f"UNKNOWN - Error: Invalid data in parameters - {e}")
            sys.exit(UNKNOWN)

    def get_opt_connected_table(self):
        """
        Generates an HTML table displaying optical port status information.
        Determines the number of ports based on the device type.

        Returns:
            str: The generated HTML table
        """
        # Retrieve device type and calculate the optical range
        device = self.parameters["device"]
        opt_range = self._get_opt_range(device)

        # Initialize the HTML table with a specified width
        table_html = "<table width='320'>"

        # Define table header with styling
        table_html += (
            "<thead>"
            "<tr align='center' style='font-size:12px;'>"
            "<th width='12%'>Port</th>"
        )

        # Add headers for remote port IDs
        for remote_number in range(1, 8 + 1):
            table_html += f"<th width='13%'>Remote {remote_number} id</th>"

        table_html += "</tr></thead>"

        # Populate table body with optical port information
        table_html += "<tbody>"
        for i in range(1, 4 + 1):
            # Construct key names to access parameter values
            connected_name = f"optical_port_devices_connected_{i}"
            opt = str(i)
            connected = self.parameters.get(connected_name, 0)

            table_html += (
                "<tr align='center' style='font-size:12px;'>"
                f"<td>opt{opt}</td>"
            )

            # Retrieve optical port device ID topology and populate IDs for connected devices
            opt_key = f"optical_port_device_id_topology_{opt}"
            for dru_connected in range(1, connected + 1):
                dru_connected_key = f"id_{dru_connected}"
                dru_id = self.parameters[opt_key].get(dru_connected_key, "-")
                table_html += f"<td>{dru_id}</td>"

            # Fill in placeholders for non-connected ports
            for id in range(connected + 1, 8 + 1):
                table_html += f"<td> - </td>"

            table_html += "</tr>"

        table_html += "</tbody></table>"

        return table_html

    def _get_opt_range(self, device):
        """
        Determines the number of optical ports based on the device type.

        Args:
            device (str): The device type (dmu_ethernet, dmu_serial, or dru_serial_service).

        Returns:
            int: The number of optical ports for the specified device
        """

        if device in ['dmu_ethernet', 'dmu_serial_service']:
            return 4
        elif device in ['dru_ethernet', 'dru_serial_service']:
            return 2
        else:
            return 4
