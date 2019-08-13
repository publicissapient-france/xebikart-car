#!/bin/bash


TUBES_DIRECTORY=${1:-$(pwd)/../xebikart-ml-tubes}

if [[ ! -d "${TUBES_DIRECTORY}" ]]; then
  echo "${TUBES_DIRECTORY} doesn't exists."
  exit 1
fi

docker run -d -v $(pwd)/workspace:/workspace -v ${TUBES_DIRECTORY}:/workspace/xebikart-ml-tubes -p 8888:8888 -p 5000:5000 xebikart_ml
