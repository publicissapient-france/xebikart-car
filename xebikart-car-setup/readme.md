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
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="<ssid>"
    psk="<password>"
}
```

## Requirements 

Setup ansible
```
pip install ansible==2.7.8
```

## Check setup
```
ansible-playbook --check --ask-pass -i inventories/cars.yml main.yml
```

## Apply setup

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
