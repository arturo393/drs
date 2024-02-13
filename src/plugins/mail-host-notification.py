#!/usr/bin/env python3

import argparse
import os
import shutil
import smtplib
import subprocess
import sys
import urllib
import syslog
from email.mime.text import MIMEText

PROG = os.path.basename(sys.argv[0])
ICINGA2HOST = os.uname().nodename
MAILBIN = 'mail'

if not shutil.which(MAILBIN):
    print(f'{MAILBIN} not found in $PATH. Consider installing it.')
    sys.exit(1)


## Function helpers
def usage():
    print('Required parameters:')
    print('  -d LONGDATETIME ($icinga.long_date_time$)')
    print('  -l HOSTNAME ($host.name$)')
    print('  -n HOSTDISPLAYNAME ($host.display_name$)')
    print('  -o HOSTOUTPUT ($host.output$)')
    print('  -r USEREMAIL ($user.email$)')
    print('  -s HOSTSTATE ($host.state$)')
    print('  -t NOTIFICATIONTYPE ($notification.type$)')
    print(
        f'Usage: {PROG} -d LONGDATETIME -l HOSTNAME -n HOSTDISPLAYNAME -o HOSTOUTPUT -r USEREMAIL -s HOSTSTATE -t NOTIFICATIONTYPE')
    sys.exit(1)


def error(msg=None):
    if msg:
        print(msg)
    usage()
    sys.exit(1)


def urlencode(s):
    return urllib.parse.quote(s, safe='')


## Main

parser = argparse.ArgumentParser(description='Send email notifications from Icinga2.')
parser.add_argument('-4', dest='HOSTADDRESS', help='$address$')
parser.add_argument('-6', dest='HOSTADDRESS6', help='$address6$')
parser.add_argument('-b', dest='NOTIFICATIONAUTHORNAME', help='$notification.author$')
parser.add_argument('-c', dest='NOTIFICATIONCOMMENT', help='$notification.comment$')
parser.add_argument('-d', dest='LONGDATETIME', required=True, help='$icinga.long_date_time$')
parser.add_argument('-f', dest='MAILFROM',
                    help='$notification_mailfrom$, requires GNU mailutils (Debian/Ubuntu) or mailx (RHEL/SUSE)')
parser.add_argument('-hs', action='store_true', help='Print this help message and exit.')
parser.add_argument('-i', dest='ICINGAWEB2URL', help='$notification_icingaweb2url$, Default: unset')
parser.add_argument('-l', dest='HOSTNAME', required=True, help='$host.name$')
parser.add_argument('-n', dest='HOSTDISPLAYNAME', required=True, help='$host.display_name$')
parser.add_argument('-o', dest='HOSTOUTPUT', required=True, help='$host.output$')
parser.add_argument('-r', dest='USEREMAIL', required=True, help='$user.email$')
parser.add_argument('-s', dest='HOSTSTATE', required=True, help='$host.state$')
parser.add_argument('-t', dest='NOTIFICATIONTYPE', required=True, help='$notification.type$')
parser.add_argument('-v', dest='VERBOSE', default=False, help='$notification_sendtosyslog$, Default: false')

args = parser.parse_args()

## Keep formatting in sync with mail-service-notification.sh
for p in ['LONGDATETIME', 'HOSTNAME', 'HOSTDISPLAYNAME', 'HOSTOUTPUT', 'HOSTSTATE', 'USEREMAIL', 'NOTIFICATIONTYPE']:
    if not getattr(args, p):
        error(f'Required parameter "{p}" is missing.')

## Build the message's subject
SUBJECT = f'[{args.NOTIFICATIONTYPE}] Host {args.HOSTDISPLAYNAME} is {args.HOSTSTATE}'

## Build the message's body
BODY = f'''
Date/Time: {args.LONGDATETIME}
Host: {args.HOSTDISPLAYNAME} ({args.HOSTNAME})
State: {args.HOSTSTATE}
Output: {args.HOSTOUTPUT}
'''

## Send the email
try:
    msg = MIMEText(BODY)
    msg['Subject'] = SUBJECT
    msg['From'] = args.MAILFROM if args.MAILFROM else f'{ICINGA2HOST}@{args.HOSTNAME}'
    msg['To'] = args.USEREMAIL

    smtp = smtplib.SMTP('localhost')
    smtp.send_message(msg)
    smtp.quit()

    print('Email sent successfully.')
except Exception as e:
    print(f'Failed to send email: {e}')
    sys.exit(1)
