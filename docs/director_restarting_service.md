**1. Create a systemd service file:**

Open a text editor and create a new file named icinga-director-monitor.service in the /etc/systemd/system directory.
Paste the following content into the file:
Fragmento de código

```
[Unit]
Description=Icinga Director Monitoring Service
After=icinga-director.service

[Service]
Type=simple
ExecStart=/bin/bash -c 'while true; do systemctl status icinga-director.service > /dev/null; if [[ $? != 0 ]]; then
systemctl restart icinga-director.service; fi; sleep 300; done'

[Install]
WantedBy=multi-user.target
Utiliza el código con precaución. Más información
```

**2. Reload systemd:**

Run the following command to reload systemd and make it aware of the new service:
Bash

```
systemctl daemon-reload
```

**3. Start the service:**

Start the service using the following command:
Bash

```
systemctl start icinga-director-monitor.service
```

**4. Enable the service (optional):**

If you want the service to start automatically at boot, enable it using:
Bash

```
systemctl enable icinga-director-monitor.service
```

