#!/bin/bash

END=${1:-"red"}
echo $END

if [ $END = "red" ]; then
	mount -t nfs -o nolock 192.168.11.207:/home/zhyang/nfs/S17P3_V2_shareDir /mnt
    sh /mnt/s17p3v2_softup_32carrier.sh
elif [ $END = "blue" ]; then
	mount -t nfs -o nolock 192.168.21.215:/storage/nfsroot/S18P2_V1_shareDir /mnt
    sh /mnt/s18p2v1_softup_broadband.sh
else
    echo "Usage: sh update.sh <red/blue>"
fi

umount /mnt
