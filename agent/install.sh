#!/bin/bash

# Employee Monitoring Agent - One-Click Installer
# This script sets up everything automatically

echo "=========================================="
echo "  Employee Monitoring Agent Installer"
echo "=========================================="
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Step 1: Check Python
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 is not installed!"
    echo "Please install Python 3 from: https://www.python.org/downloads/"
    exit 1
fi
echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Step 2: Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Step 3: Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Step 4: Install dependencies
echo "Installing required packages..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✓ All packages installed"
echo ""

# Step 5: Get JWT token
if [ ! -f ".env" ] || ! grep -q "JWT_TOKEN" .env; then
    echo "=========================================="
    echo "  First Time Setup - Login Required"
    echo "=========================================="
    echo ""
    python3 get_token.py
    echo ""
fi

# Step 6: Create desktop shortcut (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Creating desktop shortcut..."
    
    # Create an AppleScript application
    cat > ~/Desktop/StartMonitoring.command << EOF
#!/bin/bash
cd "$SCRIPT_DIR"
source venv/bin/activate
python3 monitor_agent.py
EOF
    
    chmod +x ~/Desktop/StartMonitoring.command
    echo "✓ Desktop shortcut created: StartMonitoring.command"
fi

echo ""
echo "=========================================="
echo "  Installation Complete! ✓"
echo "=========================================="
echo ""
echo "To start monitoring:"
echo "  1. Double-click 'StartMonitoring.command' on your Desktop"
echo "  OR"
echo "  2. Run: ./start_monitoring.sh"
echo ""
echo "The agent will open your dashboard automatically."
echo "Click 'Start Monitoring' in the dashboard to begin."
echo ""
