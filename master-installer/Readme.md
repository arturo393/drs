# RDSS Master installation

## Local Dependencies

Install sshpass `apt get install git sshpass`

Install ansible locally

Please refer to:
[Installing Ansible on specific operating systems](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#installing-ansible-on-specific-operating-systems)

## Get repository

Download repository from Git `git clone https://gitlab.com/itaum/rdss2.git`

## Setting up deploy environment

Enter ansible folder ``cd ./rdss2/ansible``

Edit `vars.yaml` file and change variables with yours

Define templates located at `playbooks/templates` as you desire

## Add all miniPCs to inventory

edit `inventory/hosts.yaml` file and add all miniPCs IPs
The content should be something like:

```txt
icinga_master:
  hosts:
    192.168.0.108:
    192.168.0.109:
    192.168.0.110:
    ...
```

## Provisioning miniPCs

Just execute:

`install.sh`

### Versions

![Versions](image.png)