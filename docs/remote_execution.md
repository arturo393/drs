# Remote command execution to Satellite

## Prepare Master Node

Get public key, usually is located at `$HOME/.ssh/id_rsa.pub`

### Generate keypair

`ssh-keygen -t rsa`

## Copy public key to Satellite/Agent Node

```
mkdir -p $REMOTEUSER_HOME/.ssh
chmod 700 $REMOTEUSER_HOME/.ssh
```

Copy content of master user public key `id_rsa.pub` to Satellite `remoteuser@<satellite-host_ip>:$REMOTEUSER_HOME/.ssh/authorized_keys`

`chmod 600 $REMOTEUSER_HOME/.ssh/authorized_keys`

## Execution from Master Node

`ssh remoteuser@<satellite-host_ip> 'check_command'`

### PHP Example

```php
<?php
system("ssh remoteuser@<satellite-host_ip> 'check_command'");
?>
...
```
