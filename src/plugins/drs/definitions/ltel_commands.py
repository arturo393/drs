from enum import Enum



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

