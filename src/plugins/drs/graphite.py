import sys

from src.plugins.drs.definitions.nagios import UNKNOWN

class Graphite:
    def __init__(self, parameters):
        self.parameters = parameters

    def display(self):
        """
        Generates the appropriate output based on the device type.

        Returns:
            str: The generated output
        """
        if self.parameters['device'] in ['dmu_ethernet', 'dru_ethernet', 'dmu_serial_service']:
            return self.dmu_output()
        elif self.parameters['device'] in ['discovery_ethernet', 'discovery_serial', 'discovery_redboard_serial']:
            return self.discovery_output()
        elif self.parameters['device'] in ['dmu_serial_host', 'dru_serial_host']:
            return self.dmu_serial_single()
        else:
            return ""

    def dru_output(self):
        graphite = ""
        if self.parameters['downlink_output_power'] == 0.0:
            self.parameters['downlink_output_power'] = "-"
        else:
            self.parameters['downlink_output_power'] = str(self.parameters['downlink_output_power'])
        pa_temperature = "Temperature=" + str(self.parameters['temperature'])
        pa_temperature += ";" + str(self.parameters['warning_temperature_threshold'])
        pa_temperature += ";" + str(self.parameters['critical_temperature_threshold'])
        dl_str = f"Downlink={self.parameters['downlink_output_power']}"
        dl_str += ";" + str(self.parameters['critical_uplink_threshold'])
        dl_str += ";" + str(self.parameters['critical_uplink_threshold'])
        vswr = "VSWR=" + self.parameters['vswr']
        up_str = f"Uplink={self.parameters['uplink_input_power']}"
        up_str += ";" + str(self.parameters['warning_uplink_threshold'])
        up_str += ";" + str(self.parameters['critical_uplink_threshold'])
        rt = "RT=" + self.parameters['rt'] + ";1000;2000"
        graphite = rt + " " + pa_temperature + " " + dl_str + " " + vswr + " " + up_str
        return graphite

    def dmu_output(self):
        """
        Constructs a graphite string with parameters data.

        Returns:
            graphite (str): The constructed graphite string.

        If any exception occurs during the operation, it will print an error message
        to stderr and exits with an UNKNOWN status. If a key is not found in self.parameters,
        it sets the respective parameter value to '-'.
        """
        try:
            # Use dict.get to safely fetch values; defaults to '-' if key is not found

            device = self.parameters.get('device', "")
            if device == "dmu_ethernet":
                downlink_input_power = self.parameters.get('uplink_input_power', "-")
                uplink_output_power = self.parameters.get('downlink_output_power', "-")
                if isinstance(uplink_output_power, (int, float)) and uplink_output_power > 20:
                    uplink_output_power = "-"

                if isinstance(downlink_input_power, (int, float)) and downlink_input_power > 20:
                    downlink_input_power = "-"
                    
                critical_downlink_threshold = str(self.parameters.get('critical_downlink_threshold', '-'))
                warning_downlink_threshold = str(self.parameters.get('warning_downlink_threshold', '-'))
                critical_uplink_threshold = str(self.parameters.get('critical_uplink_threshold', '-'))
                warning_uplink_threshold = str(self.parameters.get('warning_uplink_threshold', '-'))

                temperature = str(self.parameters.get('temperature', '-'))
                warning_temperature_threshold = str(self.parameters.get('warning_temperature_threshold', '-'))
                critical_temperature_threshold = str(self.parameters.get('critical_temperature_threshold', '-'))

                # Structure graphite string using fetched parameters
                dl_str = f"Downlink={downlink_input_power};{warning_downlink_threshold};{critical_downlink_threshold}"
                up_str = f"Uplink={uplink_output_power};{warning_uplink_threshold};{critical_uplink_threshold}"
                temperature_str = f"Temperature={temperature};{warning_temperature_threshold};{critical_temperature_threshold}"
                graphite = f"{dl_str} {up_str} {temperature_str}"
            else:
                uplink_input_power = self.parameters.get('uplink_input_power', "-")
                downlink_output_power = self.parameters.get('downlink_output_power', "-")

                if isinstance(uplink_input_power, (int, float)) and uplink_input_power > 20:
                    uplink_input_power = "-"

                if isinstance(downlink_output_power, (int, float)) and downlink_output_power > 20:
                    downlink_output_power = "-"

                critical_downlink_threshold = str(self.parameters.get('critical_downlink_threshold', '-'))
                warning_downlink_threshold = str(self.parameters.get('warning_downlink_threshold', '-'))
                critical_uplink_threshold = str(self.parameters.get('critical_uplink_threshold', '-'))
                warning_uplink_threshold = str(self.parameters.get('warning_uplink_threshold', '-'))

                temperature = str(self.parameters.get('temperature', '-'))
                warning_temperature_threshold = str(self.parameters.get('warning_temperature_threshold', '-'))
                critical_temperature_threshold = str(self.parameters.get('critical_temperature_threshold', '-'))

                # Structure graphite string using fetched parameters
                dl_str = f"Downlink={downlink_output_power};{warning_downlink_threshold};{critical_downlink_threshold}"
                up_str = f"Uplink={uplink_input_power};{warning_uplink_threshold};{critical_uplink_threshold}"
                temperature_str = f"Temperature={temperature};{warning_temperature_threshold};{critical_temperature_threshold}"
                graphite = f"{dl_str} {up_str} {temperature_str}"

            return graphite

        except Exception as e:
            # Handle any unexpected exception, write error message to stderr & exit
            sys.stderr.write(f"UNKNOWN - Error: {str(e)}")
            sys.exit(UNKNOWN)

    def discovery_output(self):
        rt = self.parameters['rt']
        dt = self.parameters['dt']
        rt_str = "RT=" + rt
        rt_str += ";" + str(1)
        rt_str += ";" + str(1)
        dt_str = "DT=" + dt
        dt_str += ";" + str(2)
        dt_str += ";" + str(2)
        graphite = rt_str + " " + dt_str
        return graphite

    def dmu_serial_single(self):
        graphite = ""
        rt_str = "RTA=" + self.parameters['rt'] + ";1000;2000"
        graphite = rt_str + " "
        return graphite

