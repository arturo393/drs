# Remote command execution to Satellite

## Prepare Master Node

Get public key, usually is located at `$HOME/.ssh/id_rsa.pub`

### Generate keypair

Only if you don't have one yet

```
ssh-keygen -t rsa
ssh-add id_rsa
```

If you get an error like `“Could not open a connection to your authentication agent.”`start “ssh-agent” as:

```
eval `ssh-agent`
```

## Copy public key to Satellite/Agent Node

```
mkdir -p $REMOTEUSER_HOME/.ssh
chmod 700 $REMOTEUSER_HOME/.ssh
```

Copy content of master user public key `id_rsa.pub` to Satellite:

`user@masterhost:~/.ssh$ scp id_rsa.pub remoteuser@remotehost.com:~/.ssh/`

### Optional: Ensure permissions on remote host

`chmod 600 $HOME/.ssh/authorized_keys`

## Execution from Master Node

`ssh remoteuser@<satellite-host_ip> 'check_command'`

### PHP Example

```php
<?php
system("ssh remoteuser@<satellite-host_ip> 'check_command'");
?>
...
```
