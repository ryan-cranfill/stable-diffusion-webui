#!/usr/bin/env bash
# This script is used to start the server if the user has not already started it.
# But only if it's between a certain time of day.
# This is to prevent the server from starting up when it is not needed.
# This script is called from the crontab.
# The crontab entry is:
# @reboot sleep 30; /home/ryan/stable-diffusion-webui/start_server_if_appropriate.sh

# Get the current time in 24 hour format.
current_time=$(date +%H%M)

# If the current time is between 5:15pm and 7am, start the server.
if [[ $current_time -ge 1715 ]] || [[ $current_time -lt 700 ]]; then
    # Start the server.
    echo "Starting server..."
    . /home/ryan/stable-diffusion-webui/start_pm2.sh
    echo "Server started via pm2."
  # Else, ensure the server is not running.
else
    # Stop the server.
    echo "Stopping server..."
    . /home/ryan/stable-diffusion-webui/stop_pm2.sh
    echo "Server stopped via pm2."
fi
