#!/bin/bash
set -e -o nounset
start_time=$(date +%s) # Start timestamp
clear
connection=$1
if [ "$connection" != "serial" ] && [ "$connection" != "ethernet" ]; then
    echo "La conexión no es válida. Saliendo del script."
    exit 1
fi
# Comprueba si Google Chrome ya está instalado
if [ $(dpkg-query -W -f='${Status}' google-chrome-stable 2>/dev/null | grep -c "ok installed") -eq 0 ]
then
    # Verifica si el archivo ya se ha descargado
    if [ -f google-chrome-stable_current_amd64.deb ]; then
        echo "El archivo ya se ha descargado."
    else
        # Descarga el último paquete .deb de Google Chrome usando wget
        echo "Descargando Google Chrome"
        wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    fi

    # Cambia la propiedad del archivo para que sea accesible por el usuario '_apt'
    echo "Cambiando la propiedad del archivo"
    sudo chown _apt /home/sigmadev/sigma-rds/master-installer/google-chrome-stable_current_amd64.deb

    # Instala las dependencias necesarias usando apt
    echo "Instalando dependencias"
    sudo apt install ./google-chrome-stable_current_amd64.deb -y

    # Elimina el archivo de paquete descargado
    echo "Eliminando el archivo de paquete descargado"
    rm -f google-chrome-stable_current_amd64.deb

else
    echo "Google Chrome ya está instalado"
fi

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
master_host=$(./read_yaml.sh vars.yaml master_host| sed 's/"//g')
hosts=($(./get_hosts.sh inventory/hosts.yaml))
# Obtener el valor del parámetro de conexión


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
    rcc run --silent --interactive --task scripting -- --variable hostname:$hostname --variable host:$ip_address --variable passwd:$admin_password --variable master_host:$master_host --variable connection:$connection setup_director.robot
    cd ../..
done

end_time=$(date +%s) # End timestamp
duration=$(((end_time - start_time)/60)) # Duration in seconds

echo "Script execution completed in ${duration} minutes."