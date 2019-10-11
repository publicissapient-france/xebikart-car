FROM python:3.6

ARG SIMULATOR_PATH=car-ml/simulators/DonkeySimLinux.zip

# Add tini
ENV TINI_VERSION v0.6.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /usr/bin/tini
RUN chmod +x /usr/bin/tini

# Create workspace
RUN mkdir -p /workspace
WORKDIR /workspace

# OpenGL Librairies
RUN apt update && apt install -y xvfb x11vnc mesa-utils libgl1-mesa-glx libopenmpi-dev ffmpeg && rm -rf /var/lib/apt/lists/*
# Override OpenGL Version (unity requires >= 3.2)
ENV MESA_GL_VERSION_OVERRIDE 3.3

# set default screen to 1 (to match xvfb display port)
ENV DISPLAY=:1

# Donkey Sim
RUN mkdir -p /sim
COPY $SIMULATOR_PATH /sim/donkey_sim.zip
RUN cd /sim && unzip donkey_sim.zip && rm -f donkey_sim.zip
ENV DONKEY_SIM_HOME /sim/
ENV DONKEY_SIM_HEADLESS 1

# Supervisor
RUN apt update && apt install -y supervisor && rm -rf /var/lib/apt/lists/*
COPY car-ml/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
RUN mkdir -p /var/log/supervisord/

# Python requirements for ml
COPY car-ml/requirements.txt .
RUN pip3 install -r requirements.txt

# MLFlow
ENV MLFLOW_TRACKING_URI file:/workspace/mlruns

# Install xebikart package
COPY car-package/setup.py /code/
COPY car-package/xebikart /code/xebikart
RUN pip3 install /code/

ENTRYPOINT ["/usr/bin/tini", "--"]

EXPOSE 8888
EXPOSE 5000

CMD ["/usr/bin/supervisord"]
