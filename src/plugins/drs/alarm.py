from .definitions.nagios import OK, CRITICAL, WARNING

DEFAULT_WARNING_UPLINK_THRESHOLD = 200
DEFAULT_CRITICAL_UPLINK_THRESHOLD = 200
DEFAULT_WARNING_DOWNLINK_THRESHOLD = 200
DEFAULT_CRITICAL_DOWNLINK_THRESHOLD = 200
DEFAULT_WARNING_TEMPERATURE_THRESHOLD = 200
DEFAULT_CRITICAL_TEMPERATURE_THRESHOLD = 200

class Alarm:
    """
    Class to manage alarm conditions and generate HTML output.
    """

    def __init__(self, parameters):
        """
        Initialize the alarm object with the provided parameters.

        Args:
            parameters (dict): A dictionary containing alarm parameters.
        """
        self.parameters = parameters

        self.uplink_power_alarm = OK
        self.downlink_power_alarm = OK
        self.temperature_alarm = OK

        # Extract alarm thresholds from parameters with default values
        self.critical_uplink_power_threshold = self.parameters.get('critical_uplink_threshold',
                                                                   DEFAULT_CRITICAL_UPLINK_THRESHOLD)
        self.warning_uplink_power_threshold = self.parameters.get('warning_uplink_threshold',
                                                                  DEFAULT_WARNING_UPLINK_THRESHOLD)
        self.critical_downlink_power_threshold = self.parameters.get('critical_downlink_threshold',
                                                                     DEFAULT_CRITICAL_DOWNLINK_THRESHOLD)
        self.warning_downlink_power_threshold = self.parameters.get('warning_downlink_threshold',
                                                                    DEFAULT_WARNING_DOWNLINK_THRESHOLD)
        self.critical_temperature_threshold = self.parameters.get('critical_temperature_threshold',
                                                                  DEFAULT_CRITICAL_TEMPERATURE_THRESHOLD)
        self.warning_temperature_threshold = self.parameters.get('warning_temperature_threshold',
                                                                 DEFAULT_WARNING_TEMPERATURE_THRESHOLD)

        self.check_alarm()

    def check_exit_code(self):

        if self.uplink_power_alarm == CRITICAL or self.downlink_power_alarm == CRITICAL or self.temperature_alarm == CRITICAL:
            return CRITICAL
        elif self.uplink_power_alarm == WARNING or self.downlink_power_alarm == WARNING or self.temperature_alarm == WARNING:
            return WARNING

    def check_alarm(self):
        """
        Check for alarm conditions and update alarm properties accordingly.

        Returns:
            str: Alarm message if any alarm condition is detected, empty string otherwise.
        """

        # Extract power and temperature values from parameters
        downlink_power = self.parameters.get('downlink_output_power', -200)
        uplink_power = self.parameters.get('uplink_input_power', -200)
        temperature = self.parameters.get('temperature', -200)

        alarm = ""

        # Check downlink power alarm conditions and update color/font size if necessary
        self._update_color_and_font_size(downlink_power, 'downlink_power')

        # Check uplink power alarm conditions and update color/font size if necessary
        self._update_color_and_font_size(uplink_power, 'uplink_power')

        # Check temperature alarm conditions and update color/font size if necessary
        self._update_color_and_font_size(temperature, 'temperature')

    def _get_value(self, parameter_value, default_value):
        """
        Retrieve the value of a parameter, using the default value if the parameter is not found or is '-'.

        Args:
            parameter_value (str): The value of the parameter from the input data.
            default_value (float): The default value to use if the parameter is not found or is '-'.

        Returns:
            float: The actual value of the parameter or the default value.
        """
        if parameter_value != '-':
            return float(parameter_value)
        else:
            return default_value

    def _update_color_and_font_size(self, value, parameter_name):
        """
        Update the color and font size properties for a specific parameter based on its value.

        Args:
            value (float): The value of the parameter to check.
            parameter_name (str): The name of the parameter to update color and font size for.
        """
        critical_threshold = getattr(self, f'critical_{parameter_name}_threshold')
        warning_threshold = getattr(self, f'warning_{parameter_name}_threshold')
        if value >= critical_threshold:
            setattr(self, f'{parameter_name}_alarm', CRITICAL)
        elif value >= warning_threshold:
            setattr(self, f'{parameter_name}_alarm', WARNING)
