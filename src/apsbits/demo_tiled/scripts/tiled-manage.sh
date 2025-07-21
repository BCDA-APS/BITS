#!/bin/bash
# init file for tiled server
#
# chkconfig: - 98 98
# description: tiled server
#
# processname: tiled_server

SHELL_SCRIPT_NAME=${BASH_SOURCE:-${0}}

PROJECT_DIR=$(dirname $(readlink -f "${SHELL_SCRIPT_NAME}"))
MANAGE="${PROJECT_DIR}/tiled-manage.sh"
LOGFILE="${PROJECT_DIR}/tiled-manage.log"
PIDFILE="${PROJECT_DIR}/tiled-manage.pid"
EXECUTABLE_SCRIPT="${PROJECT_DIR}/in-screen.sh"
STARTER_SCRIPT=start-tiled.sh
RETVAL=0
SLEEP_DELAY=1.5  # wait for process, sometimes
TILED_CONDA_ENV=tiled


activate_conda(){
    if [ "${CONDA_EXE}" == "" ]; then
        echo "Need CONDA_EXE defined to activate '${TILED_CONDA_ENV}' environment."
        echo "That is defined by activating *any* conda environment."
        exit 1
    fi
    CONDA_ROOT=$(dirname $(dirname $(readlink -f "${CONDA_EXE}")))
    source "${CONDA_ROOT}/etc/profile.d/conda.sh"
    conda activate "${TILED_CONDA_ENV}"
}


get_pid(){
    PID=$(/bin/cat "${PIDFILE}")
    return $PID
}


function pid_is_running(){
	get_pid
	if [ "${PID}" == "" ]; then
		# no PID in the PIDFILE
		RETVAL=1
	else
		RESPONSE=$(ps -p ${PID} -o comm=)
		if [ "${RESPONSE}" == "${STARTER_SCRIPT}" ]; then
			# PID matches the tiled server profile
			RETVAL=0
		else
			# PID is not tiled server
			RETVAL=1
		fi
	fi
	return "${RETVAL}"
}


start(){
    activate_conda
    cd "${PROJECT_DIR}"
    "${EXECUTABLE_SCRIPT}" 2>&1 >> "${LOGFILE}" &
    sleep "${SLEEP_DELAY}"
    PID=$(pidof -x ${STARTER_SCRIPT})
    /bin/echo "${PID}" > "${PIDFILE}"
    /bin/echo \
        "# [$(/bin/date -Is) $0] started ${PID}: ${EXECUTABLE_SCRIPT}" \
        2>&1 \
        >> "${LOGFILE}" &
    sleep "${SLEEP_DELAY}"
    tail -1 "${LOGFILE}"
}


stop(){
    get_pid

    if pid_is_running; then
    	/bin/echo "# [$(/bin/date -Is) $0] stopping ${PID}: ${EXECUTABLE_SCRIPT}" 2>&1 >> ${LOGFILE} &
    	kill "${PID}"
    else
		/bin/echo "# [$(/bin/date -Is) $0] not running ${PID}: ${EXECUTABLE_SCRIPT}" 2>&1 >> ${LOGFILE} &
    fi
    sleep "${SLEEP_DELAY}"
    tail -1 "${LOGFILE}"

    /bin/cp -f /dev/null "${PIDFILE}"
}


restart(){
    stop
    start
}


status(){
    if pid_is_running; then
		echo "# [$(/bin/date -Is) $0] running fine, so it seems"
    else
		echo "# [$(/bin/date -Is) $0] could not identify running process ${PID}"
    fi
}


checkup(){
    # 'crontab -e` to add entries for automated (re)start
    #=====================
    # call periodically (every 5 minutes) to see if tiled server is running
    #=====================
    #	     field	    allowed values
    #	   -----	  --------------
    #	   minute	  0-59
    #	   hour 	  0-23
    #	   day of month   1-31
    #	   month	  1-12 (or names, see below)
    #	   day of week    0-7 (0 or 7 is Sun, or use names)
    #
    # */5 * * * * /home/beams/JEMIAN/Documents/projects/BCDA-APS/tiled-template/tiled-manage.sh checkup 2>&1 > /dev/null

    if pid_is_running; then
		echo "# [$(/bin/date -Is) $0] running fine, so it seems" 2>&1 > /dev/null
    else
		echo "# [$(/bin/date -Is) $0] could not identify running process ${PID}, starting new process" 2>&1 >> "${LOGFILE}"
		start
    fi
}


case "$1" in
    start)    start ;;
    stop)     stop ;;
    restart)  restart ;;
    checkup)  checkup ;;
    status)   status ;;
    *)
        echo $"Usage: $0 {start|stop|restart|checkup|status}"
        exit 1
esac
