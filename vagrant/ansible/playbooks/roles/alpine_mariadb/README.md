# Ansible Role: MariaDB

Installs MariaDB on Alpine linux servers.

## Requirements

None.

## Role Variables

Available variables are listed below, along with default values (see `defaults/main.yml`):

```
mariadb_version: '10.6'
```

### Settings user priviledges on databases and tables

To define user priviledges use the following format:

```
db.table:priv1,priv2
```

Idempotent solution for multiple priviledges (@see http://stackoverflow.com/a/22959760)

```
mysql_privileges:
  - db1.*:ALL,GRANT
  - db2.*:USAGE

mariadb_host_users:
  - name: 'user1'
    password: 'travis'
    priv={{ mysql_privileges|join('/') }}
    hosts:
      - localhost
      - 127.0.0.1
```

### Available variables for default, hosts and groups

```
mariadb_default_users: []
mariadb_host_users: []
mariadb_group_users: []

mariadb_default_databases: []
mariadb_host_databases: []
mariadb_group_databases: []
```

### Security

This role sets an administrative user and removes root entirely. Please define the following settings:

```
mariadb_admin_home: '/root'
mariadb_admin_user: 'admin'
mariadb_admin_password: 'Set strong password here!'
```

_When a custom admin username is used, a password must be set!_

## Dependencies

None.

## Example Playbook

    - hosts: server
      roles:
        - { role: ytannus.alpine_mariadb }

## Remove User

To remove a user define `state: absent`

```
mariadb_host_users:
   - name: 'test'
     host: localhost
     password: 'test'
     priv: '*.*:ALL'
     state: 'absent'
```

## Supported OS

- Alpine Linux 3.15

## Supported MariaDB versions

- 10.6

## Required ansible version

Ansible 2.12+

## License

[MIT License](http://choosealicense.com/licenses/mit/)
