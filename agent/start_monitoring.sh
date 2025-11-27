#!/bin/bash

# Start Monitoring Agent
# Double-click this file to start the monitoring agent

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment
source venv/bin/activate

# Run the agent
python3 monitor_agent.py
