#!/bin/bash
# Agent Startup Script with Diagnostics

echo "=========================================="
echo "MONITORING AGENT STARTUP"
echo "=========================================="

# Check if backend is running
echo -e "\n[1/5] Checking backend..."
if curl -s http://localhost:5001/api >/dev/null 2>&1; then
    echo "✓ Backend is running"
else
    echo "✗ Backend is NOT running!"
    echo "  Start it with: cd backend && source venv/bin/activate && python app.py"
    exit 1
fi

# Check .env file
echo -e "\n[2/5] Checking .env configuration..."
if [ -f ".env" ]; then
    echo "✓ .env file exists"
    echo "  Contents:"
    cat .env | sed 's/PASSWORD=.*/PASSWORD=***/'
else
    echo "✗ .env file missing!"
    echo "  Creating from .env.example..."
    cp .env.example .env
    echo "  Please edit .env with your credentials"
    exit 1
fi

# Test credentials
echo -e "\n[3/5] Testing credentials..."
source venv/bin/activate
python -c "
import os, requests
from dotenv import load_dotenv
load_dotenv()

email = os.getenv('EMAIL')
password = os.getenv('PASSWORD')
api_url = os.getenv('API_URL')

if not email or not password or email == 'employee@example.com':
    print('✗ Credentials not configured!')
    print('  Edit .env file with correct EMAIL and PASSWORD')
    exit(1)

res = requests.post(f'{api_url}/auth/login', json={'email': email, 'password': password})
if res.status_code == 200:
    print(f'✓ Credentials valid for: {email}')
else:
    print(f'✗ Login failed: {res.status_code}')
    print(f'  Response: {res.text}')
    exit(1)
"

if [ $? -ne 0 ]; then
    exit 1
fi

# Check permissions (macOS)
echo -e "\n[4/5] Checking macOS permissions..."
echo "⚠ Make sure Terminal has Accessibility permissions:"
echo "  System Settings → Privacy & Security → Accessibility"
echo "  Add and enable your Terminal app"

# Start agent
echo -e "\n[5/5] Starting monitoring agent..."
echo "=========================================="
echo ""
python monitor_agent.py
