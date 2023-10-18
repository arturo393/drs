#!/bin/bash

echo "Please enter the host:"
read host

ping -c 1 $host > /dev/null 2>&1
while [ $? -ne 0 ]
do
    echo "Host is not reachable. Please enter a valid host:"
    read host
    ping -c 1 $host > /dev/null 2>&1
done

echo "Are you sure you want to use $host as the host? (y/n)"
read answer

while [ "$answer" != "y" ] && [ "$answer" != "n" ]
do
    echo "Please enter y or n:"
    read answer
done

if [ "$answer" == "n" ]
then
    echo "Please enter the host:"
    read host

    ping -c 1 $host > /dev/null 2>&1
    while [ $? -ne 0 ]
    do
        echo "Host is not reachable. Please enter a valid host:"
        read host
        ping -c 1 $host > /dev/null 2>&1
    done
fi

echo "Please enter the ansible_host:"
read ansible_host

echo "Are you sure you want to use $ansible_host as the ansible_host? (y/n)"
read answer

while [ "$answer" != "y" ] && [ "$answer" != "n" ]
do
    echo "Please enter y or n:"
    read answer
done

if [ "$answer" == "n" ]
then
    echo "Please enter the ansible_host:"
    read ansible_host
fi

echo "Which type of connection do you want to use? (serial/ethernet)"
read connection_type

while [ "$connection_type" != "serial" ] && [ "$connection_type" != "ethernet" ]
do
    echo "Please enter 'serial' or 'ethernet':"
    read connection_type
done

echo "Are you sure you want to use $connection_type as the connection? (y/n)"
read answer

while [ "$answer" != "y" ] && [ "$answer" != "n" ]
do
    echo "Please enter y or n:"
    read answer
done

if [ "$answer" == "n" ]
then
    echo "Please enter the ansible_host:"
    read connection_type
fi

# Store the sudo password in a variable (replace 'YourPassword' with the actual password)
password="Admin.123"
echo "$password" | sudo -S uname -a
echo | sudo apt-add-repository ppa:ansible/ansible 
sudo apt update
sudo apt upgrade -y
sudo apt install ansible wget git sshpass vim curl -y 

git clone https://arturo33:gitlab393@gitlab.com/itaum/sigma-rds.git
cd ./sigma-rds/
git checkout development
cd ./master-installer/inventory 
cat <<EOF > hosts.yaml 
icinga_master:
  hosts:
    $ansible_host:
      ansible_host: $host
      ansible_port: 22 
EOF

cd ..
sed -i "/icinga2_monitor_hostname:/ s/.*/icinga2_monitor_hostname: \"$ansible_host\"/" ./vars.yaml
sed -i "/icinga2_monitor_host:/ s/.*/icinga2_monitor_host: \"$host\"/" ./vars.yaml


./install.sh "$connection_type"


