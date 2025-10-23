#!/bin/bash
SHELL_SCRIPT_NAME=${BASH_SOURCE:-${0}}
SCRIPT_DIR="$(dirname $(readlink -f  "${SHELL_SCRIPT_NAME}"))"
CONFIGS_DIR=$(readlink -f "${SCRIPT_DIR}/../src/demo_instrument/configs")
ENV_FILE=$(readlink -f "${SCRIPT_DIR}/../.env")

# 2. Check if the .env file exists and source it
if [ -f "$ENV_FILE" ]; then
    # 'source' loads the variables from the file into the script's environment
    source "$ENV_FILE"
else
    echo "Error: .env file not found at $ENV_FILE" >&2
    exit 1
fi

# 3. Check if the key was actually loaded
if [ -z "$TILED_API_KEY" ]; then
    echo "Error: TILED_API_KEY variable was not found in $ENV_FILE" >&2
    exit 1
fi

# 4. Now $TILED_API_KEY is populated and can be used in your command
tiled serve config "$CONFIGS_DIR/my_config_file.yml" --api-key "$TILED_API_KEY"
