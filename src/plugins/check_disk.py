#!/usr/bin/env python3
import psutil
import sys

OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3


def check_disk_usage():
    """Checks the disk space usage of the system and returns a status message, a state code, and the Nagios state output.

    Returns:
      A tuple containing a status message, a state code, and the Nagios state output.
    """

    # Get the disk usage information.
    disk_usage = psutil.disk_usage("/")

    # Calculate the warning and critical disk sizes in GB.
    warning_disk_size_gb = disk_usage.total * 0.8
    critical_disk_size_gb = disk_usage.total * 0.9

    # Check the disk usage against the warning and critical thresholds.
    if disk_usage.used > critical_disk_size_gb:
        status_message = "CRITICAL: Disk usage is {} GB, free space is {} GB".format(
            round(disk_usage.used / 1024 ** 3, 2), round(disk_usage.free / 1024 ** 3, 2))
        state_code = CRITICAL
    elif disk_usage.used > warning_disk_size_gb:
        status_message = "WARNING: Disk usage is {} GB, free space is {} GB".format(
            round(disk_usage.used / 1024 ** 3, 2), round(disk_usage.free / 1024 ** 3, 2))
        state_code = WARNING
    else:
        status_message = "OK: Disk usage is {} GB, free space is {} GB".format(round(disk_usage.used / 1024 ** 3, 2),
                                                                               round(disk_usage.free / 1024 ** 3, 2))
        state_code = OK

    # Generate the Nagios state output.
    nagios_state_output = "|diskused={:.2f};{:.2f};{:.2f};0;{:.2f}".format(round(disk_usage.used / 1024 ** 3, 2),
                                                                           round(warning_disk_size_gb / 1024 ** 3, 2),
                                                                           round(critical_disk_size_gb / 1024 ** 3, 2),
                                                                           round(disk_usage.total / 1024 ** 3, 2))

    return status_message, state_code, nagios_state_output


if __name__ == "__main__":
    status_message, state_code, nagios_state_output = check_disk_usage()

    # Print the status message, exit with the state code, and print the Nagios state output.
    print(status_message)
    print(nagios_state_output)
    sys.exit(state_code)
