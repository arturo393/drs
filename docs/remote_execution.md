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

### Shell Example

```
/home/ytannus $❯ uname -a
Darwin Jinks.local 21.4.0 Darwin Kernel Version 21.4.0: Tue Jan 18 13:02:01 PST 2022; root:xnu-8020.100.406.0.1~18/RELEASE_X86_64 x86_64

/home/ytannus $❯ ssh sigmadev@192.168.60.78 'uname -a'
Linux drs 5.15.24-0-lts #1-Alpine SMP Thu, 17 Feb 2022 19:01:03 +0000 x86_64 Linux
```
