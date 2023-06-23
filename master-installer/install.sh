#!/bin/sh

# Setup icinga2 and Icingaweb2
ansible-playbook --ask-pass -K step1.yaml
# cd rpa/1 && rcc run --task "Setup Icingaweb2" --silent
cd rpa/setup_icingaweb2 && rcc run --task "Setup Icingaweb2" && cd ../..

# Setup extras
ansible-playbook --ask-pass -K step2.yaml
cd rpa/setup_extras && rcc run && cd ../..