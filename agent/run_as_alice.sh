#!/bin/bash
# Script to run a second agent for Alice
# This simulates a second employee on the same machine

echo "=========================================="
echo "STARTING AGENT FOR: Alice"
echo "=========================================="

# Override environment variables for this process only
export EMAIL="strawhatluff124@gmail.com"
export PASSWORD="password123"
export API_URL="http://localhost:5001/api"

# Activate virtual environment and run agent
source venv/bin/activate
python monitor_agent.py
