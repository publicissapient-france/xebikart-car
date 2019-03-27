# Xebikart-car-setup

This repository contains setup configuration.

## Requirements

Before deploying configuration, disk image must be configured following [these instructions](http://docs.donkeycar.com/guide/install_software/#get-the-raspberry-pi-working).

```
pip install ansible==2.7.8
```

## Check
```
ansible-playbook \
    --check \
    --ask-pass \
    -i inventories/cars.yml \
    main.yml
```

## Apply

```
ansible-playbook \
    --ask-pass \
    -i inventories/cars.yml \
    main.yml
```

## Apply (app only)

```
ansible-playbook \
    --ask-pass \
    -i inventories/cars.yml \
    main-app.yml
```

## Apply (car1 only)

```
ansible-playbook \
    --ask-pass \
    -i inventories/cars.yml \
    -l car1 \
    main-app.yml
```
