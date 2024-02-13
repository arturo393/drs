#!/usr/bin/env python3
import psutil
import sys

WARNINGMEMPERCENTAGE = 70
CRITICALMEMPERCENTAGE = 90

OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3


def check_memory_usage():
    """Checks the memory usage of the system and returns a status message, a state code, and the Icinga-check output without swap memory.

    Returns:
      A tuple containing a status message, a state code, and the Icinga-check output without swap memory.
    """

    # Get the memory usage information.
    memory_usage = psutil.virtual_memory()

    # Calculate the used and free memory percentages.
    used_memory_percentage = (memory_usage.used / memory_usage.total) * 100
    free_memory_percentage = (memory_usage.free / memory_usage.total) * 100

    # Generate the status message.
    status_message = "OK: {}% memory used".format(round(used_memory_percentage, 2))

    # Generate the Icinga-check output without swap memory.
    icinga_check_output = "|usedmem={:.2f};0.000;0.000;0; freemem={:.2f};0.000;0.000;0;".format(used_memory_percentage,
                                                                                                free_memory_percentage)

    # Determine the state code.
    state_code = OK
    if used_memory_percentage > CRITICALMEMPERCENTAGE:
        status_message = "CRITICAL: {}% memory used".format(round(used_memory_percentage, 2))
        state_code = CRITICAL
    elif used_memory_percentage > WARNINGMEMPERCENTAGE:
        status_message = "WARNING: {}% memory used".format(round(used_memory_percentage, 2))
        state_code = WARNING
    return status_message, state_code, icinga_check_output


if __name__ == "__main__":
    status_message, state_code, icinga_check_output = check_memory_usage()

    # Print the status message, Icinga-check output, and exit with the state code.
    print(status_message)
    print(icinga_check_output)
    sys.exit(state_code)
