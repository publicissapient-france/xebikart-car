# Download simulator

Go to : https://github.com/xebia-france/xebikart-unity/releases/download/v0.2/DonkeySimLinux.zip

And put in `car-ml/simulators/`

# Build docker image

	docker build -t xebikart_ml . -f car-ml/Dockerfile

# Start docker image with your workspace

	cd car-ml && ./start-docker.sh

Then open your browser on http://localhost:8888/

## Special Thanks

# Credits
- https://github.com/tawnkramer/donkey_gym
- https://github.com/araffin/learning-to-drive-in-5-minutes
- https://github.com/r7vme/learning-to-drive-in-a-day
