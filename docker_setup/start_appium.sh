#!/bin/bash

BL='\033[0;34m'
G='\033[0;32m'
RED='\033[0;31m'
YE='\033[1;33m'
NC='\033[0m' # No Color

function start_appium () {
    if [ "$APPIUM_PORT" == "" ] || [ "$APPIUM_PORT" == null ];
    then
    printf "${G}==>  ${YE}No port provided, instance will run on 4723 ${G}<==${NC}""\n"
    sleep 0.5
    appium 
    else
    printf "${G}==>  ${BL}Instance will run on ${YE}${APPIUM_PORT} ${G}<==${NC}""\n"
    sleep 0.5
    appium -p $APPIUM_PORT
    fi
};

start_appium