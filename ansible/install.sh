#!/bin/bash
ansible_user="sigmadev"
admin_password="Admin.123"

ansible-playbook main.yaml --extra-vars "ansible_user=$ansible_user ansible_password=$admin_password ansible_sudo_pass=$admin_password"
