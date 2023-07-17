#!/bin/bash

#!/bin/bash
set -e -o nounset
start_time=$(date +%s) # Start timestamp
clear
#Install RCC
#############################################################################
rcc_url="https://downloads.robocorp.com/rcc/releases/latest/linux64/rcc"
rcc_target_directory="/usr/local/bin"
rcc_file_name="rcc"
# Check if the file already exists in the target directory
if [[ -f "${rcc_target_directory}/${rcc_file_name}" ]]; then
    echo "RCC file already exists. Skipping download."
else
    # Download the file using curl
    sudo curl -o "${rcc_target_directory}/${rcc_file_name}" "${rcc_url}"

    # Set the permissions of the downloaded file to a+x
    sudo chmod a+x "${rcc_target_directory}/${rcc_file_name}"

    echo "RCC installation complete."
fi
#############################################################################
hosts=($(./get_hosts.sh inventory/hosts.yaml))
ansible_user=$(./read_yaml.sh vars.yaml icinga2_monitor_user| sed 's/"//g')
admin_password=$(./read_yaml.sh vars.yaml admin_password| sed 's/"//g')
host=$(./read_yaml.sh vars.yaml icinga2_monitor_host| sed 's/"//g')


ansible-playbook main.yaml --extra-vars "ansible_user=$ansible_user ansible_password=$admin_password ansible_sudo_pass=$admin_password"

for ((i = 0; i< ${#hosts[@]}; i+=2)); do
    # Extract hostname and IP address from the result variable
    hostname=${hosts[i]}
    address=${hosts[i+1]}
    echo "Setting up Director: $host"
    echo "\tPlease wait until rcc setup is finished...browser will open..."
    cd rpa/setup_extras
    rcc run --silent --interactive --task scripting -- --variable hostname:$hostname --variable address:$address --variable host:$host --variable passwd:$admin_password setup_director.robot
    cd ../..
done

end_time=$(date +%s) # End timestamp
duration=$(((end_time - start_time)/60)) # Duration in seconds

echo "Script execution completed in ${duration} minutes."