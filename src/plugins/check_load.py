#!/usr/bin/env python3
import sys
import psutil

WARNINGLOAD = 2.0
CRITICALLOAD = 5.0

OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3


def check_load_average():
    """Checks the system load average and returns a status message, a state code, and the load1min, load5min, and load15min values.

    Returns:
      A tuple containing a status message, a state code, and the load1min, load5min, and load15min values.
    """

    # Get the system load average.

    load = psutil.getloadavg()
    load_1_min, load_5_min, load_15_min = load
    # Determine the state code.
    if load_1_min > CRITICALLOAD or load_5_min > CRITICALLOAD or load_15_min > CRITICALLOAD:
        status_msg = "CRITICAL: Load averages: 1min={:.2f}, 5min={:.2f}, 15min={:.2f}".format(load_1_min,
                                                                                              load_5_min,
                                                                                              load_15_min)
        return_code = CRITICAL
    elif load_1_min > WARNINGLOAD or load_5_min > WARNINGLOAD or load_15_min > WARNINGLOAD:
        status_msg = "WARNING: Load averages: 1min={:.2f}, 5min={:.2f}, 15min={:.2f}".format(load_1_min, load_5_min,
                                                                                             load_15_min)
        return_code = WARNING
    else:
        status_msg = "OK: Load averages: 1min={:.2f}, 5min={:.2f}, 15min={:.2f}".format(load_1_min, load_5_min,
                                                                                        load_15_min)
        return_code = OK

    return status_msg, return_code, load_1_min, load_5_min, load_15_min


if __name__ == "__main__":
    status_message, state_code, load1min, load5min, load15min = check_load_average()

    # Print the status message, Icinga-check output, and exit with the state code.
    print(status_message)
    print(
        "|load1min={:.2f};{:.2f};{:.2f}; load5min={:.2f};{:.2f};{:.2f}; load15min={:.2f};{:.2f};{:.2f}".format(load1min,
                                                                                                               WARNINGLOAD,
                                                                                                               CRITICALLOAD,
                                                                                                               load5min,
                                                                                                               WARNINGLOAD,
                                                                                                               CRITICALLOAD,
                                                                                                               load15min,
                                                                                                               WARNINGLOAD,
                                                                                                               CRITICALLOAD))
    sys.exit(state_code)
