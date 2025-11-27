#!/bin/bash

# Employee Monitoring Agent - Easy Setup
# This script helps employees set up and run the monitoring agent

echo "========================================="
echo "  Employee Monitoring Agent Setup"
echo "========================================="
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "First time setup - Getting your JWT token..."
    echo ""
    python3 get_token.py
    echo ""
fi

# Check if .env has JWT_TOKEN
if [ -f ".env" ] && grep -q "JWT_TOKEN" .env; then
    echo "✓ Configuration found!"
    echo ""
    echo "Starting monitoring agent..."
    echo "The agent will:"
    echo "  1. Connect to the dashboard"
    echo "  2. Wait for you to click 'Start Monitoring'"
    echo "  3. Automatically start capturing when you do"
    echo ""
    echo "Press Ctrl+C to stop the agent"
    echo ""
    python3 monitor_agent.py
else
    echo "✗ Setup incomplete. Please run: python3 get_token.py"
fi
