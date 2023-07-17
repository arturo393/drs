#!/bin/bash

# Path to the YAML file
yaml_file=$1

# Extract the children of "hosts"
#children=$(grep -A9999 "hosts:" "$yaml_file" | awk '/^[[:blank:]]+[[:alnum:]_.-]+:/{gsub(/:/, "", $1); print $1}' | sed '/hosts/d')
#children=$(grep -E "^[[:space:]]+[0-9]" "$yaml_file" | cut -d':' -f1 | sed 's/^[[:space:]]*//')
#children=$(cat inventory/hosts.yaml | grep "ansible_host:" |  grep -Eo '([0-9]{1,3}\.){3}[0-9]{1,3}')
# Extract the hostnames and IP addresses
# Initialize an empty variable
output=""

# Extract the hostnames and IP addresses
while IFS= read -r line
do
  # Check if the line starts with a hostname
  if [[ $line =~ ^\ +([a-zA-Z0-9_-]+):$ ]]; then
    hostname=${BASH_REMATCH[1]}
  fi
  
  # Check if the line contains the ansible_host field
  if [[ $line =~ ^\ *ansible_host:\ +([0-9.]+)$ ]]; then
    ip_address=${BASH_REMATCH[1]}
    
    # Append the hostname and IP address to the output variable
    output+=" $hostname $ip_address"
  fi
done < "$yaml_file"


# Remove leading whitespace
output=${output# }

# Print the generated output
echo "$output"