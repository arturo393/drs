from abc import ABC

from src.plugins.drs.comunication_protocol.comunication_protocol import CommunicationProtocol
from src.plugins.drs.definitions.santone_commands import ResponseFlag


class LTELProtocolBase(CommunicationProtocol, ABC):
    """
    Base class for LTEL protocols, handling common LTEL frame structures.

    This class abstracts the common elements of LTELProtocol and LTELProtocolGroup,
    reducing redundancy and improving maintainability.
    """

    START_FLAG = "7E"
    UNKNOWN1 = 0x0101
    SITE_NUMBER = 0
    UNKNOWN2 = 0x0100
    TX_RX = 0x80
    UNKNOWN3 = 0x01
    MESSAGE_TYPE = 0x02
    TX_RX2 = 0xFF
    RESPOND_FLAG_INDEX = 10

    def __init__(self, dru_id: int):
        """Initialize LTELProtocolBase object."""
        super().__init__()
        self.dru_id = dru_id

    def _generate_common_header(self) -> str:
        """Generate the common header for LTEL frames."""
        return (
            f"{self.UNKNOWN1:04X}"
            f"{self.SITE_NUMBER:08X}"
            f"{self.dru_id}"
            f"{self.UNKNOWN2:04X}"
            f"{self.TX_RX:02X}"
            f"{self.UNKNOWN3:02X}"
            f"{self.MESSAGE_TYPE:02X}"
            f"{self.TX_RX2:02X}"
        )

    def _generate_ltel_frame(self, command_unit: str) -> str:
        """Generate a complete LTEL frame with checksum."""
        crc = self.generate_checksum(command_unit)
        return (
            f"{self.START_FLAG}{command_unit}{crc}{self.START_FLAG}{self.START_FLAG}"
        )

    def _is_valid_reply(self, reply: bytearray) -> bool:
        """Check if the reply is valid."""
        if not reply:
            return False

        self._response_flag = reply[self.RESPOND_FLAG_INDEX]
        return self._response_flag == ResponseFlag.SUCCESS.value
