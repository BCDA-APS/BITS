#!/bin/bash

# run the tiled server

MY_DIR=$(realpath "$(dirname $0)")
LOG_FILE="${MY_DIR}/logfile.txt"
HOST=0.0.0.0  # access server by "localhost", hostname, or IP number
# HOST="${HOSTNAME}"  # only access server by this exact name
PORT=8020

source ${CONDA_PREFIX}/etc/profile.d/conda.sh
CONDA_ENV=tiled
conda activate "${CONDA_ENV}"


# strace -fe openat,lstat \

tiled serve config \
    --port ${PORT} \
    --host ${HOST} \
    --public \
    "${MY_DIR}/config.yml" \
    2>&1 | tee "${LOG_FILE}"
