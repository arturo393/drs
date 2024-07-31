from src.plugins.drs.comunication_protocol import CommunicationProtocol


class LTELProtocolBase(CommunicationProtocol):
    """
    Base class for LTEL protocols, handling common LTEL frame structures.

    This class abstracts the common elements of LTELProtocol and LTELProtocolGroup,
    reducing redundancy and improving maintainability.
    """

    START_FLAG = "7E"
    UNKNOWN1 = 0x0101
    SITE_NUMBER = 0
    UNKNOWN2 = 0x0100

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
        )

    def _generate_ltel_frame(self, command_unit: str) -> str:
        """Generate a complete LTEL frame with checksum."""
        crc = self.generate_checksum(command_unit)
        return (
            f"{self.START_FLAG}{command_unit}{crc}{self.START_FLAG}{self.START_FLAG}"
        )
