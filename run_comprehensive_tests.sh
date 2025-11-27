#!/bin/bash

# Comprehensive Application Testing Script
# This script will start the backend, frontend, and run all tests

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Configuration
BACKEND_DIR="backend"
FRONTEND_DIR="frontend"
BACKEND_PORT=3535
FRONTEND_PORT=5173

echo -e "${BOLD}${CYAN}========================================${NC}"
echo -e "${BOLD}${CYAN}  Comprehensive Application Testing${NC}"
echo -e "${BOLD}${CYAN}========================================${NC}\n"

# Function to print section headers
print_header() {
    echo -e "\n${BOLD}${BLUE}>>> $1${NC}\n"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Function to check if port is in use
check_port() {
    lsof -ti:$1 > /dev/null 2>&1
}

# Function to kill process on port
kill_port() {
    if check_port $1; then
        print_warning "Killing existing process on port $1"
        lsof -ti:$1 | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# Cleanup function
cleanup() {
    print_header "Cleaning up..."
    
    # Kill backend
    if [ ! -z "$BACKEND_PID" ]; then
        print_warning "Stopping backend server (PID: $BACKEND_PID)"
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    # Kill frontend
    if [ ! -z "$FRONTEND_PID" ]; then
        print_warning "Stopping frontend server (PID: $FRONTEND_PID)"
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    # Kill any remaining processes on ports
    kill_port $BACKEND_PORT
    kill_port $FRONTEND_PORT
    
    print_success "Cleanup complete"
}

# Set trap to cleanup on exit
trap cleanup EXIT INT TERM

# Check prerequisites
print_header "Checking Prerequisites"

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    exit 1
fi
print_success "Python 3 found: $(python3 --version)"

# Check Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed"
    exit 1
fi
print_success "Node.js found: $(node --version)"

# Check npm
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed"
    exit 1
fi
print_success "npm found: $(npm --version)"

# Check PostgreSQL
if ! command -v psql &> /dev/null; then
    print_warning "PostgreSQL client not found - database tests may fail"
else
    print_success "PostgreSQL client found"
fi

# Check if backend directory exists
if [ ! -d "$BACKEND_DIR" ]; then
    print_error "Backend directory not found: $BACKEND_DIR"
    exit 1
fi

# Check if frontend directory exists
if [ ! -d "$FRONTEND_DIR" ]; then
    print_error "Frontend directory not found: $FRONTEND_DIR"
    exit 1
fi

# Kill any existing processes on ports
print_header "Preparing Ports"
kill_port $BACKEND_PORT
kill_port $FRONTEND_PORT
print_success "Ports are ready"

# Setup Backend
print_header "Setting Up Backend"

cd $BACKEND_DIR

# Check if virtual environment exists
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    print_warning "Virtual environment not found, creating one..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi
print_success "Virtual environment activated"

# Check if requirements are installed
if ! python -c "import flask" 2>/dev/null; then
    print_warning "Installing backend dependencies..."
    pip install -q -r requirements.txt
    print_success "Backend dependencies installed"
else
    print_success "Backend dependencies already installed"
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found, copying from .env.example"
    cp .env.example .env
    print_warning "Please configure .env file with your settings"
fi

# Check database connection
print_header "Checking Database Connection"
if python -c "from models import db; from app import create_app; app = create_app(); app.app_context().push(); db.engine.connect()" 2>/dev/null; then
    print_success "Database connection successful"
else
    print_error "Database connection failed"
    print_warning "Please ensure PostgreSQL is running and configured correctly"
    print_warning "You can continue, but database-related tests will fail"
fi

# Start Backend Server
print_header "Starting Backend Server"
python app.py > ../backend.log 2>&1 &
BACKEND_PID=$!
print_success "Backend server started (PID: $BACKEND_PID)"

# Wait for backend to be ready
echo -n "Waiting for backend to be ready"
for i in {1..30}; do
    if curl -s http://localhost:$BACKEND_PORT/api/health > /dev/null 2>&1; then
        echo ""
        print_success "Backend is ready"
        break
    fi
    echo -n "."
    sleep 1
    if [ $i -eq 30 ]; then
        echo ""
        print_error "Backend failed to start within 30 seconds"
        print_warning "Check backend.log for errors"
        exit 1
    fi
done

cd ..

# Setup Frontend
print_header "Setting Up Frontend"

cd $FRONTEND_DIR

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    print_warning "Installing frontend dependencies..."
    npm install
    print_success "Frontend dependencies installed"
else
    print_success "Frontend dependencies already installed"
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    print_warning "Creating frontend .env file"
    echo "VITE_API_URL=http://localhost:$BACKEND_PORT/api" > .env
fi

# Start Frontend Server
print_header "Starting Frontend Server"
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
print_success "Frontend server started (PID: $FRONTEND_PID)"

# Wait for frontend to be ready
echo -n "Waiting for frontend to be ready"
for i in {1..30}; do
    if curl -s http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
        echo ""
        print_success "Frontend is ready"
        break
    fi
    echo -n "."
    sleep 1
    if [ $i -eq 30 ]; then
        echo ""
        print_error "Frontend failed to start within 30 seconds"
        print_warning "Check frontend.log for errors"
        exit 1
    fi
done

cd ..

# Display server information
print_header "Server Information"
echo -e "${BOLD}Backend:${NC}  http://localhost:$BACKEND_PORT"
echo -e "${BOLD}Frontend:${NC} http://localhost:$FRONTEND_PORT"
echo -e "${BOLD}API:${NC}      http://localhost:$BACKEND_PORT/api"

# Run API Tests
print_header "Running API Tests"

cd $BACKEND_DIR

# Install test dependencies if needed
if ! python -c "import requests" 2>/dev/null; then
    print_warning "Installing requests library for testing..."
    pip install -q requests
fi

if ! python -c "from PIL import Image" 2>/dev/null; then
    print_warning "Installing Pillow library for testing..."
    pip install -q Pillow
fi

# Run comprehensive API tests
print_success "Starting comprehensive API tests..."
echo ""
python comprehensive_api_test.py

cd ..

# Manual testing instructions
print_header "Manual Testing Instructions"

echo -e "${BOLD}The servers are now running. You can perform manual testing:${NC}\n"
echo -e "1. ${CYAN}Open your browser:${NC} http://localhost:$FRONTEND_PORT"
echo -e "2. ${CYAN}Test Registration:${NC} Create admin and employee accounts"
echo -e "3. ${CYAN}Test Login:${NC} Login with different roles"
echo -e "4. ${CYAN}Test Organization Dashboard:${NC} (Admin only)"
echo -e "   - View employees"
echo -e "   - Manage monitoring configs"
echo -e "   - View sessions and screenshots"
echo -e "5. ${CYAN}Test Employee Dashboard:${NC}"
echo -e "   - Start/stop sessions"
echo -e "   - View personal data"
echo -e "   - Generate workflows"
echo -e ""
echo -e "${BOLD}Logs:${NC}"
echo -e "  Backend:  ${YELLOW}tail -f backend.log${NC}"
echo -e "  Frontend: ${YELLOW}tail -f frontend.log${NC}"
echo -e ""
echo -e "${BOLD}${YELLOW}Press Ctrl+C to stop all servers and exit${NC}\n"

# Keep script running
while true; do
    sleep 1
    
    # Check if backend is still running
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        print_error "Backend server has stopped unexpectedly"
        print_warning "Check backend.log for errors"
        break
    fi
    
    # Check if frontend is still running
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        print_error "Frontend server has stopped unexpectedly"
        print_warning "Check frontend.log for errors"
        break
    fi
done
