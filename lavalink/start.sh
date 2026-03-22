#!/bin/sh

echo "Checking for updates"
python3 /opt/Lavalink/plugin_updater.py

echo "Starting Lavalink"
exec java -jar Lavalink.jar