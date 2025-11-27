#!/bin/bash

echo "=========================================="
echo "   EMPLOYEE MONITORING AGENT SETUP"
echo "=========================================="

# 1. Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    echo "   Please install Python 3 from https://www.python.org/downloads/"
    echo "   and try again."
    read -p "Press Enter to exit..."
    exit 1
fi

# 2. Setup Virtual Environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# 3. Activate and Install Dependencies
source venv/bin/activate
echo "⬇️  Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1

# 4. Check Configuration
if [ ! -f ".env" ]; then
    echo "⚠️  Configuration file (.env) not found!"
    echo "   Creating one for you..."
    cp .env.example .env
    
    echo ""
    echo "📝 Please enter your credentials:"
    read -p "   Email: " email
    read -s -p "   Password: " password
    echo ""
    
    # Update .env file
    # Note: This is a simple replacement, might be better to let them edit it manually if complex
    # But for ease of use, we'll try to sed it if it matches the example structure
    
    # We will just append or rewrite for simplicity to ensure it works
    echo "API_URL=http://<YOUR_SERVER_IP>/api" > .env
    echo "DASHBOARD_URL=http://<YOUR_SERVER_IP>" >> .env
    echo "EMAIL=$email" >> .env
    echo "PASSWORD=$password" >> .env
    
    echo "✅ Configuration saved."
    echo "⚠️  IMPORTANT: Please ask your manager for the correct SERVER IP address"
    echo "   and update the API_URL and DASHBOARD_URL in the .env file."
    open .env
fi

# 5. Run Agent
echo "🚀 Starting Agent..."
echo "   (Keep this window open while working)"
echo "=========================================="
python monitor_agent.py
