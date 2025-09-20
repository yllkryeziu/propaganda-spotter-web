#!/bin/bash

# Main startup script for Propaganda Spotter

# Check if setup has been run
if [ ! -d "backend/venv" ] || [ ! -d "frontend/node_modules" ]; then
    echo "⚠️ Project not set up. Please run the setup script first."
    echo "👉 To set up, run: ./setup.sh"
    exit 1
fi

# All good, start the development environment
./start_dev.sh
