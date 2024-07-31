import abc
import time
import serial
import socket
import sys

from typing import Optional, Tuple, Union

from src.plugins.drs.definitions.nagios import CRITICAL

class Transceiver(abc.ABC):
    """
    Abstract base class for Transceivers, providing a common interface for
    sending and receiving data over various protocols.
    """

    @abc.abstractmethod
    def transmit_and_receive(self, commands: list, **kwargs) -> Union[dict, int]:
        """
        Abstract method for transmitting commands and receiving responses.

        Args:
            commands (list): A list of commands to be transmitted.
            **kwargs: Additional keyword arguments specific to the protocol.

        Returns:
            Union[dict, int]: A dictionary containing response data, or an integer
                               indicating the number of successful operations,
                               depending on the protocol.
        """
        pass


