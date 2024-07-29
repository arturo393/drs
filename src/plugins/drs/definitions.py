from enum import IntEnum, Enum

OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3

# Define constant values
DEFAULT_WARNING_UPLINK_THRESHOLD = 200
DEFAULT_CRITICAL_UPLINK_THRESHOLD = 200
DEFAULT_WARNING_DOWNLINK_THRESHOLD = 200
DEFAULT_CRITICAL_DOWNLINK_THRESHOLD = 200
DEFAULT_WARNING_TEMPERATURE_THRESHOLD = 200
DEFAULT_CRITICAL_TEMPERATURE_THRESHOLD = 200

fix_ip_end = 0x16
fix_ip_end_opt_1 = 0x64
fix_ip_end_opt_2 = 0x78
fix_ip_end_opt_3 = 0x8C
fix_ip_end_opt_4 = 0xA0

SET = 1
QUERY_GROUP = 0
QUERY_SINGLE = 3

ETHERNET = 0
SERIAL = 1

DONWLINK_MODULE = 0 << 7
UPLINK_MODULE = 1 << 7


class DataType(IntEnum):
    DATA_INITIATION = 0x00
    RESPONSE = 0x01
    INTERMEDIATE_FREQUENCY = 0x02
    IF_BOARD_RESPONSE = 0X03


class ResponseFlag(IntEnum):
    SUCCESS = 0x00
    WRONG_COMMAND_NUMBER = 0x01
    COMMAND_DATA_ERROR = 0x02
    COMMAND_BODY_LENGTH_ERROR = 0x03
    OPERATION_FAILED = 0x04
    OTHER_FAILURES = 0X05
    DATA_SIZE_EXCEEDS = 0X06


class HardwarePeripheralDeviceParameterCommand(IntEnum):
    version_number = 0x01
    temperature = 0x02
    hardware_status = 0x03
    ad5662 = 0x05
    afc = 0x07
    datt = 0x09
    vcxo_manual = 0x0e
    vcxo_compensation_enable_step_delay_reference_value = 0x1e
    rx0_broadband_power = 0x20
    rx1_broadband_power = 0x21
    #    q_dac0 = 0x26
    dac1 = 0x28
    _9524 = 0x2a
    _1197a = 0x2c
    _1197b = 0x2e
    test_control_register = 0xca
    eth_ip_address = 0xcc
    module_equipment_number = 0xce
    broadband_switching = 0x81
    reboot_device = 0xd0


class NearEndSettingCommandNumber(IntEnum):
    optical_port_switch = 0x90
    NETWORK_MODE_CONFIG = 0x92
    MAC_ADDRESS = 0x94
    DEVICE_ID = 0x96
    DELAY_TARGET_POSITION = 0x98
    # Add more setting command numbers


class NearEndQueryCommandNumber(IntEnum):
    optical_port_switch = 0x91
    network_mode_config = 0x93
    mac_address = 0x95
    device_id = 0x97
    delay_target_position = 0x99
    optical_port_status = 0x9a
    optical_port_device_id_topology_1 = 0x9b
    actual_delay_optical_port_1 = 0x9c
    optical_port_mac_topology_1 = 0x9d
    optical_port_device_id_topology_2 = 0x9e
    actual_delay_optical_port_2 = 0x9f
    optical_port_mac_topology_2 = 0xa0
    optical_port_device_id_topology_3 = 0xa1
    actual_delay_optical_port_3 = 0xa2
    optical_port_mac_topology_3 = 0xa3
    optical_port_device_id_topology_4 = 0xa4
    actual_delay_optical_port_4 = 0xa5
    optical_port_mac_topology_4 = 0xa6
    optical_module_hw_parameters = 0xa7


# Add more query command numbers
class RemoteQueryCommandNumber(IntEnum):
    # Queries
    optical_port_switch = 0xb1
    network_mode = 0xb3
    mac_address = 0xb5
    device_id = 0xb7
    delay = 0xb9
    gain_compensation = 0xbb
    optical_port_status = 0xbc
    near_end_port_location = 0xbd
    channel_0_optical_network_mode = 0xbe
    channel_1_optical_network_mode = 0xbf
    optical_module_hardware_parameters = 0xc0
    own_topology_id = 0xfe


class RemoteSettingCommandNumber(IntEnum):
    optical_port_switch = 0xb0
    network_mode = 0xb2
    mac_address = 0xb4
    device_id = 0xb6
    delay = 0xb8
    gain_compensation = 0xba


class Rx0QueryCmd(IntEnum):
    broadband_power = 0x20
    channel_frequency_configuration = 0x36
    alc = 0x38
    carrier_search_results = 0x39
    carrier_power_value_after_carrier_search = 0x3a
    compensation_enable_switch = 0x3c
    gain_compensation = 0x3e
    temperature_compensation_table = 0x40
    channel_switch = 0x42
    filter_compensation = 0x43
    frequency_point_compensation = 0x45
    bottom_noise = 0x47
    input_power_peak = 0x49
    alc_control_difference_threshold = 0x4c
    baseband_gain = 0x4e
    central_frequency_point = 0xeb
    subband_bandwidth = 0xed
    bottom_noise_channel_switch = 0xf1
    uplink_noise_suppression_switch = 0xf4
    uplink_noise_suppression_threshold = 0xf6
    uplink_noise_suppression_threshold_correction_value = 0xfc
    mean_exp_search_num = 0x83
    frequency_synchronization_switch = 0x85
    rx0_iir_bandwidth = 0xf6


class Rx0SettingCmd(IntEnum):
    central_frequency_point = 0x22
    channel_frequency_configuration = 0x35
    alc = 0x37
    compensation_enable_switch = 0x3b
    gain_compensation = 0x3d
    temperature_compensation_table = 0x3f
    channel_switch = 0x41
    filter_compensation = 0x43
    frequency_point_compensation = 0x45
    bottom_noise = 0x47
    alc_control_difference_threshold = 0x4b
    baseband_gain = 0x4d
    subband_bandwidth = 0xd0
    bottom_noise_channel_switch = 0xf2
    uplink_noise_suppression_switch = 0xf5
    uplink_noise_suppression_threshold = 0xf7
    uplink_noise_suppression_threshold_correction_value = 0xfd
    mean_exp_search_num = 0x82
    frequency_synchronization_switch = 0x84
    rx0_iir_bandwidth = 0xed


class Tx0QueryCmd:
    compensation_enable_switch = 0x71
    gain_compensation = 0x73
    temperature_compensation_table = 0x75
    filter_compensation = 0x79
    peak_output_power = 0x7a
    downlink_output_power = 0xe5
    gain_power_control_att = 0xef
    power_offset = 0xea
    input_and_output_power = 0xf3


class Tx0SettingCmd:
    compensation_enable_switch = 0x70
    gain_compensation = 0x71
    temperature_compensation_table = 0x74
    filter_compensation = 0x78
    peak_output_power = 0x7a
    gain_power_control_att = 0xe7


class Tx1QueryCmd:
    compensation_enable_switch = 0x80
    gain_compensation = 0x82
    temperature_compensation_table = 0x84
    filter_compensation = 0x88
    peak_output_power = 0x8a
    gain_power_control_att = 0xe8


class Tx1SettingCmd:
    compensation_enable_switch = 0x80
    gain_compensation = 0x82
    temperature_compensation_table = 0x84
    filter_compensation = 0x88
    peak_output_power = 0x8a
    gain_power_control_att = 0xe8

class DRSMasterCommand(IntEnum):
    optical_port_devices_connected_1 = 0xf8
    optical_port_devices_connected_2 = 0xf9
    optical_port_devices_connected_3 = 0xfa
    optical_port_devices_connected_4 = 0xfb
    input_and_output_power = Tx0QueryCmd.input_and_output_power
    channel_switch = Rx0QueryCmd.channel_switch
    channel_frequency_configuration = Rx0QueryCmd.channel_frequency_configuration
    central_frequency_point = Rx0QueryCmd.central_frequency_point
    broadband_switching = HardwarePeripheralDeviceParameterCommand.broadband_switching
    gain_power_control_att = Tx0QueryCmd.gain_power_control_att
    optical_port_switch = NearEndQueryCommandNumber.optical_port_switch
    optical_port_status = NearEndQueryCommandNumber.optical_port_status
    subband_bandwidth = Rx0QueryCmd.subband_bandwidth
    rx0_broadband_power = HardwarePeripheralDeviceParameterCommand.rx0_broadband_power
    rx1_broadband_power = HardwarePeripheralDeviceParameterCommand.rx1_broadband_power
    # optical_module_hw_parameters = NearEndQueryCommandNumber.optical_module_hw_parameters
    # rx0_iir_bandwidth = Rx0QueryCmd.rx0_iir_bandwidth
    temperature = HardwarePeripheralDeviceParameterCommand.temperature
#    datt = HardwarePeripheralDeviceParameterCommand.datt


class DRSRemoteCommand(IntEnum):
    temperature = HardwarePeripheralDeviceParameterCommand.temperature
    input_and_output_power = Tx0QueryCmd.input_and_output_power
    channel_switch = Rx0QueryCmd.channel_switch
    channel_frequency_configuration = Rx0QueryCmd.channel_frequency_configuration
    central_frequency_point = Rx0QueryCmd.central_frequency_point
    broadband_switching = HardwarePeripheralDeviceParameterCommand.broadband_switching
    gain_power_control_att = Tx0QueryCmd.gain_power_control_att
    optical_port_switch = NearEndQueryCommandNumber.optical_port_switch
    optical_port_status = NearEndQueryCommandNumber.optical_port_status
    subband_bandwidth = Rx0QueryCmd.subband_bandwidth
    rx0_broadband_power = HardwarePeripheralDeviceParameterCommand.rx0_broadband_power
    rx1_broadband_power = HardwarePeripheralDeviceParameterCommand.rx1_broadband_power
    optical_module_hw_parameters = NearEndQueryCommandNumber.optical_module_hw_parameters
    optical_port_devices_connected_1 = DRSMasterCommand.optical_port_devices_connected_1
    optical_port_devices_connected_2 = DRSMasterCommand.optical_port_devices_connected_2
    optical_port_devices_connected_3 = DRSMasterCommand.optical_port_devices_connected_3
    optical_port_devices_connected_4 = DRSMasterCommand.optical_port_devices_connected_4
    #rx0_iir_bandwidth = Rx0QueryCmd.rx0_iir_bandwidth


class DRSRemoteSerialCommand(IntEnum):
    optical_port_device_id_topology_1 = NearEndQueryCommandNumber.optical_port_device_id_topology_1
    optical_port_device_id_topology_2 = NearEndQueryCommandNumber.optical_port_device_id_topology_2
    optical_port_device_id_topology_3 = NearEndQueryCommandNumber.optical_port_device_id_topology_3
    optical_port_device_id_topology_4 = NearEndQueryCommandNumber.optical_port_device_id_topology_4


class DiscoveryCommand(IntEnum):
    optical_port_devices_connected_1 = DRSMasterCommand.optical_port_devices_connected_1
    optical_port_devices_connected_2 = DRSMasterCommand.optical_port_devices_connected_2
    optical_port_devices_connected_3 = DRSMasterCommand.optical_port_devices_connected_3
    optical_port_devices_connected_4 = DRSMasterCommand.optical_port_devices_connected_4
    # eth_ip_address = HardwarePeripheralDeviceParameterCommand.eth_ip_address
    device_id = NearEndQueryCommandNumber.device_id
    optical_port_device_id_topology_1 = NearEndQueryCommandNumber.optical_port_device_id_topology_1
    optical_port_device_id_topology_2 = NearEndQueryCommandNumber.optical_port_device_id_topology_2
    optical_port_device_id_topology_3 = NearEndQueryCommandNumber.optical_port_device_id_topology_3
    optical_port_device_id_topology_4 = NearEndQueryCommandNumber.optical_port_device_id_topology_4
    optical_port_mac_topology_1 = NearEndQueryCommandNumber.optical_port_mac_topology_1
    optical_port_mac_topology_2 = NearEndQueryCommandNumber.optical_port_mac_topology_2
    optical_port_mac_topology_3 = NearEndQueryCommandNumber.optical_port_mac_topology_3
    optical_port_mac_topology_4 = NearEndQueryCommandNumber.optical_port_mac_topology_4


class DiscoveryRedBoardCommand(IntEnum):
    optical_port_devices_connected_1 = DRSMasterCommand.optical_port_devices_connected_1
    optical_port_devices_connected_2 = DRSMasterCommand.optical_port_devices_connected_2
    optical_port_devices_connected_3 = DRSMasterCommand.optical_port_devices_connected_3
    optical_port_devices_connected_4 = DRSMasterCommand.optical_port_devices_connected_4
    # eth_ip_address = HardwarePeripheralDeviceParameterCommand.eth_ip_address
    device_id = NearEndQueryCommandNumber.device_id
    optical_port_device_id_topology_1 = NearEndQueryCommandNumber.optical_port_device_id_topology_1
    optical_port_device_id_topology_2 = NearEndQueryCommandNumber.optical_port_device_id_topology_2
    optical_port_device_id_topology_3 = NearEndQueryCommandNumber.optical_port_device_id_topology_3
    optical_port_device_id_topology_4 = NearEndQueryCommandNumber.optical_port_device_id_topology_4
    optical_port_mac_topology_1 = NearEndQueryCommandNumber.optical_port_mac_topology_1
    optical_port_mac_topology_2 = NearEndQueryCommandNumber.optical_port_mac_topology_2
    optical_port_mac_topology_3 = NearEndQueryCommandNumber.optical_port_mac_topology_3
    optical_port_mac_topology_4 = NearEndQueryCommandNumber.optical_port_mac_topology_4


class SettingCommand(IntEnum):
    gain_power_control_att = Tx0SettingCmd.gain_power_control_att
    channel_switch = Rx0SettingCmd.channel_switch
    optical_port_switch = NearEndSettingCommandNumber.optical_port_switch
    broadband_switching = 0x80
    channel_frequency_configuration = Rx0SettingCmd.channel_frequency_configuration


class CommBoardCmd(Enum):
    channel_switch_bit = (0x05, 0x160A)
    channel_1_number = (0x05, 0x1004)
    channel_2_number = (0x05, 0x1104)
    channel_3_number = (0x05, 0x1204)
    channel_4_number = (0x05, 0x1304)
    channel_5_number = (0x05, 0x1404)
    channel_6_number = (0x05, 0x1504)
    channel_7_number = (0x05, 0x1604)
    channel_8_number = (0x05, 0x1704)
    channel_9_number = (0x05, 0x1804)
    channel_10_number = (0x05, 0x1904)
    channel_11_number = (0x05, 0x1a04)
    channel_12_number = (0x05, 0x1b04)
    channel_13_number = (0x05, 0x1c04)
    channel_14_number = (0x05, 0x1d04)
    channel_15_number = (0x05, 0x1e04)
    channel_16_number = (0x05, 0x1f04)
    uplink_att = (0x04, 0x4004)
    downlink_att = (0x04, 0x4104)
    working_mode = (0x04, 0xEF0B)
    downlink_vswr = (0x04, 0x0605)
    downlink_output_power = (0x04, 0x0305)
    uplink_input_power = (0x04, 0x2505)
    power_amplifier_temperature = (0x04, 0x0105)
    uplink_start_frequency = (0x07, 0x180A)
    downlink_start_frequency = (0x07, 0x190A)
    work_bandwidth = (0x07, 0x1A0A)
    channel_bandwidth = (0x07, 0x1B0A)


class ChannelCommBoardCmd(Enum):
    channel_switch_bit = (0x05, 0x160A)
    channel_1_number = (0x05, 0x1004)
    channel_2_number = (0x05, 0x1104)
    channel_3_number = (0x05, 0x1204)
    channel_4_number = (0x05, 0x1304)
    channel_5_number = (0x05, 0x1404)
    channel_6_number = (0x05, 0x1504)
    channel_7_number = (0x05, 0x1604)
    channel_8_number = (0x05, 0x1704)
    channel_9_number = (0x05, 0x1804)
    channel_10_number = (0x05, 0x1904)
    channel_11_number = (0x05, 0x1a04)
    channel_12_number = (0x05, 0x1b04)
    channel_13_number = (0x05, 0x1c04)
    channel_14_number = (0x05, 0x1d04)
    channel_15_number = (0x05, 0x1e04)
    channel_16_number = (0x05, 0x1f04)


class FreqCommBoardCmd(Enum):
    uplink_start_frequency = (0x07, 0x180A)
    # downlink_start_frequency = (0x07, 0x190A)
    work_bandwidth = (0x07, 0x1A0A)
    channel_bandwidth = (0x07, 0x1B0A)


class ParametersCommBoardCmd(Enum):
    # rf_power_sitch = (0x04,0x0104)
    uplink_att = (0x04, 0x4004)
    downlink_att = (0x04, 0x4104)
    working_mode = (0x04, 0xEF0B)
    downlink_vswr = (0x04, 0x0605)
    downlink_output_power = (0x04, 0x0305)
    uplink_input_power = (0x04, 0x2505)
    power_amplifier_temperature = (0x04, 0x0105)


class CommBoardGroupCmd(Enum):
    channel = ''.join([f"{cmd.value[0]:02X}{cmd.value[1]:04X}0000" for cmd in ChannelCommBoardCmd])
    parameters = ''.join([f"{cmd.value[0]:02X}{cmd.value[1]:04X}00" for cmd in ParametersCommBoardCmd])
    frequencies = ''.join([f"{cmd.value[0]:02X}{cmd.value[1]:04X}00000000" for cmd in FreqCommBoardCmd])

