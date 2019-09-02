# Xebikart-car-setup

This repository contains setup configuration.

Before deploying configuration, disk image must be configured following [these instructions](http://docs.donkeycar.com/guide/install_software/#get-the-raspberry-pi-working).

For convenience, here are the main steps:

## Prepare SD card

Download image available [here](https://drive.google.com/open?id=1vr4nEXLEh4xByKAXik8KhK3o-XWgo2fQ) and unzip it.

Copy image to SD card (replace **diskX** and **rdiskX** with **appropriate** identifier):
**/!\\** command below will reset all data in **diskX** **/!\\**
```
diskutil list
diskutil unmountDisk /dev/diskX
sudo dd bs=1m if=donkey_2.5.0_pi3.img of=/dev/rdiskX conv=sync
```

## Setup Wifi

Create `/wpa_supplicant.conf` file inside SD card boot volume with content like following:
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

## Expand filesystem

Connect to pi via ssh. 
```
ssh pi@192.168.1.{101,102}
$ sudo raspi-config
```
Then go to `Advanced Options` > `Expand Filesystem > Finish` and reboot.

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