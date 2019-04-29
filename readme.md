# XebiKart Car

## Car setup

See instructions here: [car setup](./xebikart-car-setup/readme.md)

## Usage (from Raspberry Pi)

Donkeycar App is deployed and started as a [systemd](https://fr.wikipedia.org/wiki/Systemd) service.

App status:
```
sudo systemctl status xebikart-car-app
```

Stop app:
```
sudo systemctl stop xebikart-car-app
```

Start app:
```
sudo systemctl start xebikart-car-app
```

App folder is located at `/home/pi/xebikart-car-app/`.
For debugging purposes app can also be started manually from previous folder:
```
./manage.py drive
```

Configuration can be updated in `config.py` file located in app folder.

**/!\\** Any update will be erased by automated app deployment if not updated in this repository.**/!\\**

## Drive car using a PS4 controller

Use left stick to control steering.
Use right stick to control throttle. To reverse throttle, stick must be pushed down **twice**.
