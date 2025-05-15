#!/bin/bash


./docker_setup/start_emu_headless.sh && uv run server/android_env_server.py 
