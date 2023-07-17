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
ansible_user=$(./read_yaml.sh vars.yaml icinga2_monitor_user| sed 's/"//g')
admin_password=$(./read_yaml.sh vars.yaml admin_password| sed 's/"//g')
hosts=($(./get_hosts.sh inventory/hosts.yaml))


# Step 1 (Base)
#############################################################################
echo "Setup Icinga & Icingaweb2 Base"
rm -rf /tmp/setup.token
ansible-playbook step1.yaml --extra-vars "ansible_user=$ansible_user ansible_password=$admin_password ansible_sudo_pass=$admin_password"
for ((i = 0; i< ${#hosts[@]}; i+=2)); do
    # Extract hostname and IP address from the result variable
    hostname=${hosts[i]}
    ip_address=${hosts[i+1]}
    echo "\tSetting up Icingaweb2: $ip_address"
    token=$(cat /tmp/setup.token/$hostname/etc/icingaweb2/setup.token)
    echo "\tPlease wait until rcc setup is finished...browser will open..."
    cd rpa/setup_icingaweb2
    rcc task run --silent --interactive --task scripting -- --variable host:$ip_address --variable passwd:$admin_password --variable token:$token setup_icingaweb2.robot
    cd ../..
done


#Step 2 (Setup extras)
############################################################################
ansible-playbook step2.yaml --extra-vars "ansible_user=$ansible_user ansible_password=$admin_password ansible_sudo_pass=$admin_password"
for ((i = 0; i< ${#hosts[@]}; i+=2)); do
    # Extract hostname and IP address from the result variable
    hostname=${hosts[i]}
    ip_address=${hosts[i+1]}
    echo "Setting up Icingaweb2 Extra Modules: $ip_address"
    echo "\tPlease wait until rcc setup is finished...browser will open..."
    cd rpa/setup_extras
    rcc run --silent --interactive --task scripting -- --variable hostname:$hostname --variable host:$ip_address --variable passwd:$admin_password tasks.robot
    cd ../..
done


# Final Step
#############################################################################
ansible-playbook playbooks/final-step.yaml --extra-vars "ansible_user=$ansible_user ansible_password=$admin_password ansible_sudo_pass=$admin_password"


# Add director basket and create Services Apply Rules
ansible-playbook step3.yaml --extra-vars "ansible_user=$ansible_user ansible_password=$admin_password ansible_sudo_pass=$admin_password"
for ((i = 0; i< ${#hosts[@]}; i+=2)); do
    # Extract hostname and IP address from the result variable
    hostname=${hosts[i]}
    ip_address=${hosts[i+1]}
    echo "Setting up Director Service Apply Rules: $ip_address"
    echo "\tPlease wait until rcc setup is finished...browser will open..."
    cd rpa/setup_extras
     rcc run --silent --interactive --task scripting -- --variable host:$ip_address --variable passwd:$admin_password setup_director.robot
    cd ../..
done

end_time=$(date +%s) # End timestamp
duration=$(((end_time - start_time)/60)) # Duration in seconds

echo "Script execution completed in ${duration} minutes."