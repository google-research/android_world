#!/bin/bash


# Credits to https://github.com/amrsa1/Android-Emulator-image

readonly G_LOG_I='[INFO]'
readonly G_LOG_W='[WARN]'
readonly G_LOG_E='[ERROR]'
BL='\033[0;34m'
G='\033[0;32m'
NC='\033[0m' # No Color

main() {
    launch_xvfb
    launch_window_manager
    run_vnc_server
    printf "${G}==> ${BL}Welcome to android-emulator VNC by amrsa ${G}<==${NC}""\n"
}

launch_xvfb() {
    # Set defaults if the user did not specify envs.
    export DISPLAY=${XVFB_DISPLAY:-:1}
    local screen=${XVFB_SCREEN:-0}
    local resolution=${XVFB_RESOLUTION:-1280x1024x24}
    local timeout=${XVFB_TIMEOUT:-5}

    # Start and wait for either Xvfb to be fully up or we hit the timeout.
    Xvfb ${DISPLAY} -screen ${screen} ${resolution} &
    local loopCount=0
    until xdpyinfo -display ${DISPLAY} > /dev/null 2>&1
    do
        loopCount=$((loopCount+1))
        sleep 1
        if [ ${loopCount} -gt ${timeout} ]
        then
            echo "${G_LOG_E} xvfb failed to start."
            exit 1
        fi
    done
}

launch_window_manager() {
    local timeout=${XVFB_TIMEOUT:-5}

    # Start and wait for either fluxbox to be fully up or we hit the timeout.
    fluxbox &
    local loopCount=0
    until wmctrl -m > /dev/null 2>&1
    do
        loopCount=$((loopCount+1))
        sleep 1
        if [ ${loopCount} -gt ${timeout} ]
        then
            echo "${G_LOG_E} fluxbox failed to start."
            exit 1
        fi
    done
}

run_vnc_server() {
    local passwordArgument='-nopw'

    if [ -n "${VNC_PASSWORD}" ]
    then
        local passwordFilePath="${HOME}/x11vnc.pass"
        if ! x11vnc -storepasswd "${VNC_PASSWORD}" "${passwordFilePath}"
        then
            echo "${G_LOG_E} Failed to store x11vnc password."
            exit 1
        fi
        passwordArgument=-"-rfbauth ${passwordFilePath}"
        echo "${G_LOG_I} The VNC server will ask for a password."
    else
        echo "${G_LOG_W} The VNC server will NOT ask for a password."
    fi

    x11vnc -ncache_cr -display ${DISPLAY} -forever ${passwordArgument} &
    wait $!
}


control_c() {
    echo ""
    exit
}

trap control_c SIGINT SIGTERM SIGHUP

main

exit