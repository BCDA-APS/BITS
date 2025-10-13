#!/bin/bash
# file: qs_host.sh
# Manage the bluesky queueserver host process.
# Could be in a screen session or run as a direct process.

SHELL_SCRIPT_NAME=${BASH_SOURCE:-${0}}
SCRIPT_DIR="$(dirname $(readlink -f  "${SHELL_SCRIPT_NAME}"))"
CONFIGS_DIR=$(readlink -f "${SCRIPT_DIR}/../demo_instrument/configs")

###-----------------------------
### Change program defaults here

# Instrument configuration YAML file with databroker catalog name.
ICONFIG_YML="${CONFIGS_DIR}"/iconfig.yml

# Bluesky queueserver configuration YAML file.
# This file contains the definition of 'redis_addr'.  (default: localhost:6379)
# "export" is for BITS to identify when QS is running.
export QS_CONFIG_YML="${SCRIPT_DIR}/qs-config.yml"

# Host name (from $hostname) where the queueserver host process runs.
# QS_HOSTNAME=amber.xray.aps.anl.gov  # if a specific host is required
QS_HOSTNAME="$(hostname)"

PROCESS=start-re-manager  # from the conda environment
STARTUP_COMMAND="${PROCESS} --config=${QS_CONFIG_YML}"

#--------------------
# internal configuration below

# echo "PROCESS=${PROCESS}"
if [ ! -f $(which "${PROCESS}") ]; then
    echo "PROCESS '${PROCESS}': file not found. CONDA_PREFIX='${CONDA_PREFIX}'"
    exit 1
fi

if [ -z "$STARTUP_DIR" ] ; then
    # If no startup dir is specified, use the directory with this script
    STARTUP_DIR="${SCRIPT_DIR}"
fi

if [ "${DATABROKER_CATALOG}" == "" ]; then
    if [ -f "${ICONFIG_YML}" ]; then
        DATABROKER_CATALOG=$(grep DATABROKER_CATALOG "${ICONFIG_YML}" | awk '{print $NF}')
        # echo "Using catalog ${DATABROKER_CATALOG}"
    fi
fi
DEFAULT_SESSION_NAME="bluesky_queueserver-${DATABROKER_CATALOG}"

#--------------------

SELECTION=${1:-usage}
SESSION_NAME=${2:-"${DEFAULT_SESSION_NAME}"}

# But other management commands will fail if mismatch
if [ "$(hostname)" != "${QS_HOSTNAME}" ]; then
    echo "Must manage queueserver process on ${QS_HOSTNAME}.  This is $(hostname)."
    exit 1
fi

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# echo "SESSION_NAME = ${SESSION_NAME}"
# echo "SHELL_SCRIPT_NAME = ${SHELL_SCRIPT_NAME}"
# echo "STARTUP_COMMAND = ${STARTUP_COMMAND}"
# echo "STARTUP_DIR = ${STARTUP_DIR}"

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

function checkpid() {
    # Assume the process is down until proven otherwise
    PROCESS_DOWN=1

    MY_UID=$(id -u)
    # The '\$' is needed in the pgrep pattern to select vm7, but not vm7.sh
    MY_PID=$(ps -u | grep "${PROCESS}")
    #!echo "MY_PID=${MY_PID}"
    SCREEN_SESSION="${MY_PID}.${SESSION_NAME}"

    if [ "${MY_PID}" != "" ] ; then
        SCREEN_PID="${MY_PID}"

        # At least one instance of the process is running;
        # Find the binary that is associated with this process
        for pid in ${MY_PID}; do
            # compare directories
            BIN_CWD=$(readlink "/proc/${pid}/cwd")
            START_CWD=$(readlink -f "${STARTUP_DIR}")

            if [ "$BIN_CWD" = "$START_CWD" ] ; then
                # The process is running with PID=$pid from $STARTUP_DIR
                P_PID=$(ps -p "${pid}" -o ppid=)
                # strip leading (and trailing) whitespace
                arr=($P_PID)
                P_PID=${arr[0]}
                SCREEN_SESSION="${P_PID}.${SESSION_NAME}"
                SCREEN_MATCH=$(screen -ls "${SCREEN_SESSION}" | grep "${SESSION_NAME}")
                if [ "${SCREEN_MATCH}" != "" ] ; then
                    # process is running in screen
                    PROCESS_DOWN=0
                    MY_PID=${pid}
                    SCREEN_PID=${P_PID}
                    break
                fi
            fi
        done
    else
        # process is not running
        PROCESS_DOWN=1
    fi

    return ${PROCESS_DOWN}
}

function checkup () {
    if ! checkpid; then
        restart
    fi
}

function console () {
    if checkpid; then
        echo "Connecting to ${SCREEN_SESSION}'s screen session"
        # The -r flag will only connect if no one is attached to the session
        #!screen -r "${SESSION_NAME}"
        # The -x flag will connect even if someone is attached to the session
        screen -x "${SCREEN_SESSION}"
    else
        echo "${SCREEN_NAME} is not running"
    fi
}

function exit_if_running() {
    # ensure that multiple, simultaneous processes are not started by this user ID
    MY_UID=$(id -u)
    MY_PID=$(pgrep "${SESSION_NAME}"\$ -u "${MY_UID}")

    if [ "" != "${MY_PID}" ] ; then
        echo "${SESSION_NAME} is already running (PID=${MY_PID}), won't start a new one"
        exit 1
    fi
}

function restart() {
    stop
    sleep 0.1  # empirical, 0.01 is too short, 1.0 is plenty.
    start
}

function run_process() {
    # only use this for diagnostic purposes
    exit_if_running
    cd "${STARTUP_DIR}"
    ${STARTUP_COMMAND}
}

function screenpid() {
    if [ -z "${SCREEN_PID}" ] ; then
        echo
    else
        echo " in a screen session (pid=${SCREEN_PID})"
    fi
}

function start() {
    if checkpid; then
        echo -n "${SCREEN_SESSION} is already running (pid=${MY_PID})"
        screenpid
    else
        if [ ! -f "${CONDA_EXE}" ]; then
            echo "No 'conda' command available."
            exit 1
        fi
        echo "Starting ${SESSION_NAME}"
        cd "${STARTUP_DIR}"
        # Run SESSION_NAME inside a screen session
        CMD="screen -DmS ${SESSION_NAME} -h 5000 ${STARTUP_COMMAND}"
        ${CMD} &
    fi
}

function status() {
    if checkpid; then
        echo -n "${SCREEN_SESSION} is running (pid=${MY_PID})"
        screenpid
    else
        echo "${SESSION_NAME} is not running"
    fi
}

function stop() {
    if checkpid; then
        echo "Stopping ${SCREEN_SESSION} (pid=${MY_PID})"
        kill "${MY_PID}"
    else
        echo "${SESSION_NAME} is not running"
    fi
}

function usage() {
    echo "Usage: $(basename "${SHELL_SCRIPT_NAME}") {start|stop|restart|status|checkup|console|run} [NAME]"
    echo ""
    echo "    COMMANDS"
    echo "        console   attach to process console if process is running in screen"
    echo "        checkup   check that process is running, restart if not"
    echo "        restart   restart process"
    echo "        run       run process in console (not screen)"
    echo "        start     start process"
    echo "        status    report if process is running"
    echo "        stop      stop process"
    echo ""
    echo "    OPTIONAL TERMS"
    echo "        NAME      name of process (default: ${DEFAULT_SESSION_NAME})"
}

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

case ${SELECTION} in
    start) start ;;
    stop | kill) stop ;;
    restart) restart ;;
    status) status ;;
    checkup) checkup ;;
    console) console ;;
    run) run_process ;;
    *) usage ;;
esac

# -----------------------------------------------------------------------------
# :author:    BCDA
# :copyright: (c) 2017-2025, UChicago Argonne, LLC
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------
