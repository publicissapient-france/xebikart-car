# Donkey dataset

## Tubes

Tubes have been recorded and are stored in https://github.com/xebia-france/xebikart-ml-tubes

To download tubes, you need [git lfs](https://help.github.com/en/articles/installing-git-large-file-storage).

    brew install git-lfs
    git lfs install

Then you can clone the repository in your workspace

    git clone git@github.com:xebia-france/xebikart-ml-tubes.git
    
Add new tubes

    # from PI
    > cd xebikart-car-app
    > cp -r tub/ tub.v5.01
    > tar -zcf tub.v5.01.tar.gz tub.v5.01
    
    # from your computer
    > scp pi@<car_ip>:/home/pi/xebikart-car-app/tub.v5.01.tar.gz .