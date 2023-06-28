#!/bin/sh

# Install RCC
#############################################################################
rcc_url="https://downloads.robocorp.com/rcc/releases/v14.6.0/linux64/rcc"
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
# ansible-playbook --ask-pass -K step1.yaml
echo "Setup Icinga & Icingaweb2 Base"
ansible-playbook step1.yaml --extra-vars "ansible_user=$ansible_user ansible_password=$admin_password ansible_sudo_pass=$admin_password"
for ip_address in "${hosts[@]}"
do
    echo "\tSeting up Icingaweb2: $ip_address"
    token=$(cat /tmp/setup.token/$ip_address/etc/icingaweb2/setup.token)
    cd rpa/setup_icingaweb2 && rcc task run --silent --interactive --task scripting -- --variable host:$ip_address --variable passwd:$admin_password --variable token:$token setup_icingaweb2.robot && cd ../..
done

exit
# Step 2 (Setup extras)
#############################################################################
pwd
ansible-playbook step2.yaml --extra-vars "ansible_user=$ansible_user ansible_password=$admin_password ansible_sudo_pass=$admin_password"
for ip_address in "${hosts[@]}"
do
    echo "Configurando Icingaweb2 Base: $ip_address"
    cd rpa/setup_extras && rcc run && cd ../..
done

