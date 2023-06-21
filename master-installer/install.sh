#!/bin/sh

# Setup icinga2 and Icingaweb2
ansible-playbook --ask-pass -K step1.yaml
# cd rpa/1 && rcc run --task "Setup Icingaweb2" --silent
cd rpa/1 && rcc run --task "Setup Icingaweb2"