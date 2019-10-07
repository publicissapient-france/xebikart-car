FROM python:3.6

ARG SIMULATOR_PATH=simulators/DonkeySimLinux.zip

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
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
RUN mkdir -p /var/log/supervisord/

# Python requirements for dev
COPY dev-requirements.txt .
RUN pip3 install -r dev-requirements.txt

# MLFlow
ENV MLFLOW_TRACKING_URI file:/workspace/mlruns

# Add tensorboard
RUN curl -sL https://deb.nodesource.com/setup_10.x | bash - && \
  apt update && apt install nodejs npm && jupyter labextension install jupyterlab_tensorboard \
  && rm -rf /var/lib/apt/lists/*

# Install xebikart requirements
COPY requirements.txt /code/
RUN pip3 install -r /code/requirements.txt

# patch for tensorflow 1.13.1 from intel-tensorflow
RUN pip3 uninstall -y intel-tensorflow Keras-Applications Keras-Preprocessing \
    && pip3 install tensorflow

# Install xebikart package
COPY setup.py /code/
COPY xebikart /code/xebikart
RUN pip3 install /code/[gym,rl]

ENTRYPOINT ["/usr/bin/tini", "--"]

EXPOSE 8888
EXPOSE 5000

CMD ["/usr/bin/supervisord"]
