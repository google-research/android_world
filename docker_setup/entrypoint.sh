#!/bin/bash


#============================================
# Install Audio Recorder apk
#============================================
function install_audio_recorder_apk() {
  adb install /tmp/app-releaseConfig-release.apk && \
  adb shell monkey -p com.dimowner.audiorecorder -c android.intent.category.LAUNCHER 1
}


./docker_setup/start_emu_headless.sh && \
adb root && \
install_audio_recorder_apk && \
python3 -m server.android_env_server
