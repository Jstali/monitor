#!/bin/bash
# Quick Start Script for Monitoring Agent
# This script helps you start the monitoring agent with proper checks

echo "======================================================================"
echo "  MONITORING AGENT - QUICK START"
echo "======================================================================"
echo ""

# Check if we're in the agent directory
if [ ! -f "monitor_agent.py" ]; then
    echo "❌ Error: Please run this script from the agent directory"
    echo "   cd /Users/stalin_j/monitor\ copy/agent"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found"
    echo "   Please create .env file with API_URL and JWT_TOKEN"
    exit 1
fi

echo "📋 Pre-flight Checks:"
echo ""

# Check Python
if command -v python3 &> /dev/null; then
    echo "✅ Python 3: $(python3 --version)"
else
    echo "❌ Python 3 not found"
    exit 1
fi

# Check required packages
echo "✅ Checking required packages..."
python3 -c "import mss, PIL, requests, psutil" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ All required packages installed"
else
    echo "⚠️  Some packages missing. Installing..."
    pip3 install -r requirements.txt
fi

echo ""
echo "======================================================================"
echo "  CHOOSE AN OPTION:"
echo "======================================================================"
echo ""
echo "  1. Run Diagnostics (Check if everything is working)"
echo "  2. Quick Test (10-second test)"
echo "  3. Full Test (30-second test with activity detection)"
echo "  4. Start Monitoring Agent (Production)"
echo "  5. Exit"
echo ""
read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo ""
        echo "Running diagnostics..."
        python3 diagnose_monitoring.py
        ;;
    2)
        echo ""
        echo "Running quick test (10 seconds)..."
        python3 quick_test.py
        ;;
    3)
        echo ""
        echo "Running full test (30 seconds)..."
        echo "Switch between applications to test detection!"
        python3 test_monitoring.py
        ;;
    4)
        echo ""
        echo "======================================================================"
        echo "  STARTING MONITORING AGENT"
        echo "======================================================================"
        echo ""
        echo "📸 Screenshot interval: 10 seconds (default)"
        echo "📊 Activity check: 5 seconds (default)"
        echo "🔄 Allowlist refresh: 30 seconds"
        echo ""
        echo "Press Ctrl+C to stop the agent"
        echo ""
        echo "======================================================================"
        echo ""
        python3 monitor_agent.py
        ;;
    5)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice. Please run again and select 1-5."
        exit 1
        ;;
esac

echo ""
echo "======================================================================"
echo "Done!"
echo "======================================================================"
