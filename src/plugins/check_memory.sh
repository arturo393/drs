  1 #!/bin/sh
  2 #
  3 # Author:  Jan Collijs
  4 # Email:   jan.collijs@inuits.eu
  5 # Date:    October 2012
  6 # Updated: December 2014 by Omar Reygaert
  7 # Updated: February 2018 by Jan Collijs
  8 #      Implemented available memory check over free memory based on /proc/meminfo
  9 # Purpose: Icinga-check to check the memory usage of the system
 10
 11 PROGNAME=`basename $0`
 12 PROGPATH=`echo $0 | sed -e 's,[\\/][^\\/][^\\/]*$,,'`
 13 REVISION=`echo '$Revision: 1.00 $' | sed -e 's/[^0-9.]//g'`
 14
 15 . $PROGPATH/utils.sh
 16
 17 WARNINGMEMPERCENTAGE=15
 18 CRITICALMEMPERCENTAGE=10
 19 WARNINGSWAOPERCENTAGE=25
 20 CRITICALSWAPPERCENTAGE=50
 21
 22 # Retrieving the data from the server
 23 TOTALMEM=`vmstat -s -SM | grep "total memory" | cut -f1 -d'M' | tr -d ' '`
 24 USEDMEM=`vmstat -s -SM | grep " active memory" | cut -f1 -d'M' | tr -d ' '`
 25 FREEMEM=`vmstat -s -SM | grep "free memory" | cut -f1 -d'M' | tr -d ' '`
 26 CACHEDMEM=`vmstat -s -SM | grep "swap cache" | cut -f1 -d's' | tr -d ' '`
 27 AVAILABLEMEM=$(cat /proc/meminfo | grep "MemAvailable" | cut -f2 -d':' | tr -s " " | cut -f2 -d
 28 AVAILABLEMEM=$(($AVAILABLEMEM / 1024 ))
 29
 30 TOTALSWAP=`vmstat -s -SM | grep "total swap" | cut -f1 -d'M' | tr -d ' '`
 31 USEDSWAP=`vmstat -s -SM | grep "used swap" | cut -f1 -d'M' | tr -d ' '`
 32 FREESWAP=`vmstat -s -SM | grep "free swap" | cut -f1 -d'M' | tr -d ' '`
 33
 34 # Calculating the percentages for memory & swap
 35 USEDMEMPERCENTAGE=$(( $USEDMEM * 100 / $TOTALMEM))
 36 FREEMEMPERCENTAGE=$(( $FREEMEM * 100 / $TOTALMEM))
 37 AVAILABLEMEMPERCENTAGE=$(( $AVAILABLEMEM * 100 / $TOTALMEM))
 38
 39 USEDSWAPPERCENTAGE=$(( $USEDSWAP * 100 / $TOTALSWAP))
 40 FREESWAPPERCENTAGE=$(( $FREESWAP * 100 / $TOTALSWAP))
 41
 42 # Compiling the memory message & icinga state
 43 if [ $AVAILABLEMEMPERCENTAGE -lt $WARNINGMEMPERCENTAGE ];then
 44   MEMMESSAGE="WARNING: only $AVAILABLEMEMPERCENTAGE% is available, $USEDMEMPERCENTAGE% of memor
 45   MSTATE=$STATE_WARNING
 46 elif [ $AVAILABLEMEMPERCENTAGE -lt $CRITICALMEMPERCENTAGE ];then
 47   MEMMESSAGE="CRITICAL: only $AVAILABLEMEMPERCENTAGE% is available, $USEDMEMPERCENTAGE% of memo
 48   MSTATE=$STATE_CRITICAL
 49 else
 50   MEMMESSAGE="OK: $AVAILABLEMEMPERCENTAGE% is available, $USEDMEMPERCENTAGE% of memory used"
 51   MSTATE=$STATE_OK
 52 fi
 53
 54 # Compiling the swap message & icinga state
 55 if [ $USEDSWAPPERCENTAGE -gt $WARNINGSWAOPERCENTAGE ];then
 56   SWAPMESSAGE="WARNING: $USEDSWAPPERCENTAGE% of swap used, only $FREESWAPPERCENTAGE% is free"
 57   SSTATE=$STATE_WARNING
 58 elif [ $USEDSWAPPERCENTAGE -gt $CRITICALSWAPPERCENTAGE ];then
 59   SWAPMESSAGE="CRITICAL: $USEDSWAPPERCENTAGE% of swap used, $FREESWAPPERCENTAGE% is free"
 60   SSTATE=$STATE_CRITICAL
 61 else
 62   SWAPMESSAGE="OK: $USEDSWAPPERCENTAGE% of swap used, $FREESWAPPERCENTAGE% is free"
 63   SSTATE=$STATE_OK
 64 fi
 65
 66 # Retrieving the correct state for icinga and distributing it
 67 if [ $SSTATE -lt 0 -o $SSTATE -gt 3 -o $MSTATE -lt 0 -o $MSTATE -gt 3 ]; then
 68   STATE=$STATE_UNKNOWN
 69   elif [ $SSTATE -eq 0 -a $MSTATE -eq 0 ]; then
 70     STATE=$STATE_OK
 71 elif [ $SSTATE -eq 1 -a $MSTATE -eq 1 ]; then
 72     STATE=$STATE_WARNING
 73 elif [ $SSTATE -eq 2 -a $MSTATE -eq 2 ]; then
 74     STATE=$STATE_CRITICAL
 75 elif [ $SSTATE -eq 3 -a $MSTATE -eq 3 ]; then
 76     STATE=$STATE_UNKNOWN
 77 elif [ $SSTATE -eq 3 -o $MSTATE -eq 3 ]; then
 78     STATE=$STATE_UNKNOWN
 79 elif [ $SSTATE -eq 2 -o $MSTATE -eq 2 ]; then
 80     STATE=$STATE_CRITICAL
 81 elif [ $SSTATE -eq 1 -o $MSTATE -eq 1 ]; then
 82     STATE=$STATE_WARNING
 83 elif [ $SSTATE -eq 0 -o $MSTATE -eq 0 ]; then
 84     STATE=$STATE_OK
 85 else
 86   STATE=$STATE_UNKNOWN
 87 fi
 88 # Distributing the ouput message and exiting with the nagios state
 89 echo "$MEMMESSAGE / $SWAPMESSAGE"
 90 #load1=0.130;0.000;0.000;0; load5=0.147;0.000;0.000;0; load15=0.175;0.000;0.000;0;^?
 91 echo "|usedmem=$USEDMEMPERCENTAGE;0.000;0.000;0; freemem=$FREEMEMPERCENTAGE;0.000;0.000;0;"
 92 exit $STATE
 93
~
~
~