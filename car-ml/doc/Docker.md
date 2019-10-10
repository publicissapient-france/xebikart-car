# Download simulator

Go to : https://github.com/xebia-france/xebikart-unity/releases/download/v0.2/DonkeySimLinux.zip

And put in `car-ml/simulators/`

# Build docker image

	docker build -t xebikart_ml .

# Start docker image with your workspace

	docker run -d -v $(pwd)/workspace:/workspace -v $(pwd)/../xebikart-ml-tubes:/workspace/xebikart-ml-tubes -p 8888:8888 -p 5000:5000 xebikart_ml

Then open your browser on http://localhost:8888/

## Special Thanks

# Credits
- https://github.com/tawnkramer/donkey_gym
- https://github.com/araffin/learning-to-drive-in-5-minutes
- https://github.com/r7vme/learning-to-drive-in-a-day
