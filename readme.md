# XebiKart Car

## Car setup

See instructions here: [car setup](car-setup/readme.md)

## Usage (from Raspberry Pi)

Connect via ssh to the car, for example for car 1:
```
$ ssh pi@192.168.1.101
```

Launch the script to drive the car:
```
cd car-app/
./manage.py
```

Configuration can be updated in `config.py` file located in app folder.

**/!\\** Any update will be erased by automated app deployment if not updated in this repository.**/!\\**

## Drive car using a PS4 controller

Use left stick to control steering.
Use right stick to control throttle. To reverse throttle, stick must be pushed down **twice**.
