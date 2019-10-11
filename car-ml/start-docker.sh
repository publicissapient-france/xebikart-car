#!/bin/bash

TUBES_DIRECTORY=${1:-$(pwd)/../xebikart-ml-tubes}
MLRUNS_DIRECTORY=${2:-$(pwd)/../xebikart-ml-runs}

if [[ ! -d "${TUBES_DIRECTORY}" ]]; then
  echo "${TUBES_DIRECTORY} doesn't exists."
  exit 1
fi
if [[ ! -d "${MLRUNS_DIRECTORY}" ]]; then
  echo "${MLRUNS_DIRECTORY} doesn't exists."
  exit 1
fi

docker run -d \
-v $(pwd)/workspace:/workspace \
-v ${TUBES_DIRECTORY}:/workspace/xebikart-ml-tubes \
-v ${MLRUNS_DIRECTORY}:/workspace/mlruns \
-p 8888:8888 -p 5000:5000 -p 5900:5900 xebikart_ml
