if [ $1 -le 6 ]; then
	mount -o nolock -t nfs 192.168.11.207:/home/zhyang/ArmLinuxApp/www /mnt
	if [ $1 -eq 1 ]; then
			cp /mnt/syspar.ini /home/
		    /home/create_db 1 /home/syspar.ini /home/syspar.db
		    cp /home/syspar.db /mnt
	elif [ $1 -eq 2 ]; then
			cp /mnt/tempcomp.ini /home/
		    /home/create_db 1 /home/tempcomp.ini /home/tempcomp.db
		    cp /home/tempcomp.db /mnt
	elif [ $1 -eq 3 ]; then
		    /home/create_db 2 /home/syspar.db /home/syspar.ini
		    cp /home/syspar.ini /mnt
	elif [ $1 -eq 4 ]; then
		    /home/create_db 2 /home/tempcomp.db /home/tempcomp.ini
		    cp /home/tempcomp.ini /mnt
	elif [ $1 -eq 5 ]; then
		    /home/create_db 1 $2 $3
		    cp $3 /mnt
	elif [ $1 -eq 6 ]; then
		    /home/create_db 2 $2 $3
		    cp $3 /mnt
	fi
	umount /mnt
elif [ $1 -eq 7 ]; then
	/home/create_db 1 /home/syspar.ini /home/syspar.db
elif [ $1 -eq 8 ]; then
	/home/create_db 1 /home/tempcomp.ini /home/tempcomp.db
elif [ $1 -eq 9 ]; then
	mount -o nolock -t nfs 192.168.11.207:/home/zhyang/ArmLinuxApp /mnt
	cp /mnt/ms_files/syspar.ini /home
	/home/create_db 1 /home/syspar.ini /home/syspar.db
	cp /home/syspar.db /mnt/ms_files
	cp /mnt/ss_files/syspar.ini /home
	/home/create_db 1 /home/syspar.ini /home/syspar.db
	cp /home/syspar.db /mnt/ss_files
	umount /mnt
fi

