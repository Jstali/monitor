#!/bin/bash

# Quick Start Script for Employee Monitoring Application

echo "=================================="
echo "Employee Monitoring Application"
echo "Quick Start Setup"
echo "=================================="
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ] || [ ! -d "agent" ]; then
    echo "Error: Please run this script from the monitor directory"
    exit 1
fi

# Backend setup
echo "📦 Setting up Backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment and installing dependencies..."
source venv/bin/activate
pip install -q -r requirements.txt

if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit backend/.env with your API key and settings"
fi

cd ..

# Frontend setup
echo ""
echo "📦 Setting up Frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

cd ..

# Agent setup
echo ""
echo "📦 Setting up Agent..."
cd agent

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment and installing dependencies..."
source venv/bin/activate
pip install -q -r requirements.txt

if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit agent/.env with employee credentials"
fi

cd ..

echo ""
echo "✅ Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Edit backend/.env with your extraction API key"
echo "2. Edit agent/.env with employee credentials"
echo ""
echo "To start the application:"
echo "  Terminal 1: cd backend && source venv/bin/activate && python app.py"
echo "  Terminal 2: cd frontend && npm run dev"
echo "  Terminal 3: cd agent && source venv/bin/activate && python monitor_agent.py"
echo ""
echo "Then open http://localhost:5173 in your browser"
echo ""
