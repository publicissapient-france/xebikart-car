# Xebikart-car-setup

This repository contains setup configuration.

Before deploying configuration, disk image must be configured following [these instructions](http://docs.donkeycar.com/guide/install_software/#get-the-raspberry-pi-working).

For convenience, here are the main steps:

## Prepare SD card

Download latest raspbian image available [here](https://downloads.raspberrypi.org/raspbian_lite_latest) and unzip it.

Copy image to SD card (replace **diskX** and **rdiskX** with **appropriate** identifier):
**/!\\** command below will reset all data in **diskX** **/!\\**
```
diskutil list
diskutil unmountDisk /dev/diskX
sudo dd bs=1m if=2019-09-26-raspbian-buster-lite.img of=/dev/rdiskX conv=sync
```

## Enable SSH

Create `/ssh` file inside SD card boot volume:
```
touch /Volumes/boot/ssh
```

## Reserve a static IP address for the car

Check [this page](https://github.com/xebia-france/xebikart-car/wiki/Configure-static-IP-address-for-Donkeycar) to see how to set up static wifi.

## Setup Wifi

Create `/Volumes/boot/wpa_supplicant.conf` file inside SD card boot volume with content below:
```
country=FR
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="<ssid>"
    psk="<password>"
}
```

Finally you can unmount SD card from your computer
```
diskutil unmountDisk /dev/diskX
```

## Configure PI

Connect to pi via ssh. 
```
ssh pi@192.168.1.{101,102,103}
$ sudo raspi-config
```

Configure following options:
1. Enable I2C: `Interfacing Options` > `I2C`
2. Enable Camera: `Interfacing Options` > `Camera`
3. Expand Filesystem: `Advanced Options` > `Expand Filesystem`
4. Apply all changes: `Finish`

Reboot pi.
```
sudo reboot
```

## Setup App (from Desktop)

### Requirements

Setup ansible
```
pip install ansible==2.7.8
```

Create a file named `ansible-vault` (git-ignored) whose content is the password to decrypt ansible-vault values.

### Check setup
```
ansible-playbook --check --ask-pass -i inventories/cars.yml main.yml
```

### Apply setup

All cars:
```
ansible-playbook --ask-pass -i inventories/cars.yml main.yml
```

Only app setup:
```
ansible-playbook --ask-pass -i inventories/cars.yml main-app.yml
```

Only app setup (car 1):
```
ansible-playbook --ask-pass -i inventories/cars.yml -l car1 main-app.yml
```

Only app setup (car 2):
```
ansible-playbook --ask-pass -i inventories/cars.yml -l car2 main-app.yml
```

Only app setup (car 3):
```
ansible-playbook --ask-pass -i inventories/cars.yml -l car3 main-app.yml
```

## Pairing a PS4 controller

### from PS4 Controller

To start pairing, simultaneously press **PS** and **Share** buttons for 5 seconds.

### from Raspberry Pi

After first setup, pi needs to be rebooted:
```
sudo reboot
```

After reboot, launch bluetooth command prompt:
```
sudo bluetoothctl
```

From bluetooth command prompt:

Car1
```
agent on
default-agent
scan on
connect 40:1B:5F:77:AC:E3
trust 40:1B:5F:77:AC:E3
quit
```

Car2
```
agent on
default-agent
scan on
connect 40:1B:5F:77:8E:13
trust 40:1B:5F:77:8E:13
quit
```

Car3
```
agent on
default-agent
scan on
connect 90:89:5F:73:0E:11
trust 90:89:5F:73:0E:11
quit
```

Example output for the commands above:
```
(env) pi@donkeypi:~ $ sudo bluetoothctl
[NEW] Controller B8:27:EB:87:CE:70 donkeypi [default]
[bluetooth]# agent on
Agent registered
[bluetooth]# default-agent
Default agent request successful
[bluetooth]# scan on
Discovery started
[CHG] Controller B8:27:EB:87:CE:70 Discovering: yes
[NEW] Device 40:1B:5F:77:AC:E3 Wireless Controller
[bluetooth]# connect 40:1B:5F:77:AC:E3
Attempting to connect to 40:1B:5F:77:AC:E3
[CHG] Device 40:1B:5F:77:AC:E3 Connected: yes
[CHG] Device 40:1B:5F:77:AC:E3 UUIDs: 00001124-0000-1000-8000-00805f9b34fb
[CHG] Device 40:1B:5F:77:AC:E3 UUIDs: 00001200-0000-1000-8000-00805f9b34fb
[CHG] Device 40:1B:5F:77:AC:E3 ServicesResolved: yes
[CHG] Device 40:1B:5F:77:AC:E3 Paired: yes
Connection successful
[Wireless Controller]# trust 40:1B:5F:77:AC:E3
[CHG] Device 40:1B:5F:77:AC:E3 Trusted: yes
Changing 40:1B:5F:77:AC:E3 trust succeeded
[Wireless Controller]# quit
```

Pairing needs to be done only once and is valid even after reboot.

## Encrypted values in Ansible

To encrypt a value:
```
ansible-vault encrypt_string 'rabbitmq_username_value' --name 'rabbitmq_username'
ansible-vault encrypt_string 'rabbitmq_password_value' --name 'rabbitmq_password'
```