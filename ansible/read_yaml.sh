#!/bin/bash

# Path to the YAML file
yaml_file=$1
yaml_variable=$2

# Function to read YAML values
read_yaml() {
    local yaml_file=$1
    local yaml_key=$2

    # Remove leading spaces from the YAML key
    local trimmed_key=$(echo "$yaml_key" | sed -e 's/^[[:space:]]*//')
    # Extract the value corresponding to the key
    local yaml_value=$(grep "$trimmed_key:" "$yaml_file" | awk -F: '{gsub(/^[ \t]+/, "", $2); print $2}')
    
    echo "$yaml_value"
}

# Read variables from the YAML file
variable_values=($(read_yaml "$yaml_file" "$yaml_variable"))

# Print the values
for value in "${variable_values[@]}"; do
    echo $value
done

