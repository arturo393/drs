#!/bin/bash

# Path to the YAML file
yaml_file=$1

# Extract the children of "hosts"
children=$(grep -A9999 "hosts:" "$yaml_file" | awk '/^[[:blank:]]+[[:alnum:]_.-]+:/{gsub(/:/, "", $1); print $1}' | sed '/hosts/d')
#children=$(grep -E "^[[:space:]]+[0-9]" "$yaml_file" | cut -d':' -f1 | sed 's/^[[:space:]]*//')
echo "$children"

