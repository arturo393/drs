# Moxa Driver

Install kernel sources and compilation tools

```
apt-get install dpkg-dev
apt-get source linux-image-$(uname -r)
apt install linux-headers-$(uname -r)
```

## Get moxa drivers

```
wget https://www.moxa.com/getmedia/57dfa4c1-8a2a-4da6-84c1-a36944ead74d/moxa-uport-1100-series-linux-kernel-5.x-driver-v5.1.tgz
```

## Install moxa drivers

```
tar xvzf moxa-uport-1100-series-linux-kernel-5.x-driver-v5.1.tgz
cd mxu11x0/
./mxinstall
```

## Verify

`lsmod|grep mxu11x0`

output should be something like:

```
mxu11x0               114688  0
usbserial              61440  1 mxu11x0
usbcore               323584  4 usbserial,mxu11x0,ehci_hcd,uhci_hcd
```

## Add sigmadev to dialout group

```
usermod -a -G dialout sigmadev

```

---

# Index

- [Readme](/readme.md)
- [Master Node](/docs/setup_master_debian.md)
- [Satellite Node](/docs/setup_satellite_debian.md)
