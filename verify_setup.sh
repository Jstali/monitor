#!/bin/bash

# Verification script for Monitor Application Setup
# Checks all configurations before deployment

set -e

echo "=========================================="
echo "Monitor Application - Setup Verification"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0

# Check 1: Docker installation
echo "1. Checking Docker installation..."
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓${NC} Docker is installed: $(docker --version)"
else
    echo -e "${RED}✗${NC} Docker is not installed"
    ERRORS=$((ERRORS + 1))
fi

# Check 2: Docker Compose
echo ""
echo "2. Checking Docker Compose..."
if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
    echo -e "${GREEN}✓${NC} Docker Compose is available"
else
    echo -e "${RED}✗${NC} Docker Compose is not installed"
    ERRORS=$((ERRORS + 1))
fi

# Check 3: .env file exists
echo ""
echo "3. Checking .env file..."
if [ -f .env ]; then
    echo -e "${GREEN}✓${NC} .env file exists"
    if grep -q "DATABASE_URL" .env; then
        echo -e "${GREEN}✓${NC} DATABASE_URL is configured"
    else
        echo -e "${RED}✗${NC} DATABASE_URL not found in .env"
        ERRORS=$((ERRORS + 1))
    fi
    if grep -q "VITE_API_URL.*3232" .env; then
        echo -e "${GREEN}✓${NC} VITE_API_URL is set to port 3232"
    else
        echo -e "${YELLOW}⚠${NC} VITE_API_URL may not be set correctly"
    fi
else
    echo -e "${RED}✗${NC} .env file not found"
    ERRORS=$((ERRORS + 1))
fi

# Check 4: PostgreSQL connection
echo ""
echo "4. Checking PostgreSQL database connection..."
if PGPASSWORD=abcd psql -h localhost -U postgres -d monitor -c "SELECT 1;" &> /dev/null; then
    echo -e "${GREEN}✓${NC} PostgreSQL database 'monitor' is accessible"
    
    # Check if tables exist
    TABLE_COUNT=$(PGPASSWORD=abcd psql -h localhost -U postgres -d monitor -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' ')
    if [ "$TABLE_COUNT" -gt "0" ]; then
        echo -e "${GREEN}✓${NC} Database has $TABLE_COUNT table(s)"
    else
        echo -e "${YELLOW}⚠${NC} Database exists but no tables found (will be created on first run)"
    fi
else
    echo -e "${RED}✗${NC} Cannot connect to PostgreSQL database"
    echo "   Make sure PostgreSQL is running and password is correct"
    ERRORS=$((ERRORS + 1))
fi

# Check 5: Port availability
echo ""
echo "5. Checking port availability..."
if ! netstat -tuln 2>/dev/null | grep -q ":3434 "; then
    echo -e "${GREEN}✓${NC} Port 3434 (frontend) is available"
else
    echo -e "${YELLOW}⚠${NC} Port 3434 is already in use"
fi

if ! netstat -tuln 2>/dev/null | grep -q ":3232 "; then
    echo -e "${GREEN}✓${NC} Port 3232 (backend) is available"
else
    echo -e "${YELLOW}⚠${NC} Port 3232 is already in use"
fi

# Check 6: Docker Compose configuration
echo ""
echo "6. Checking docker-compose.yml..."
if [ -f docker-compose.yml ]; then
    echo -e "${GREEN}✓${NC} docker-compose.yml exists"
    
    if grep -q '"3434:80"' docker-compose.yml; then
        echo -e "${GREEN}✓${NC} Frontend port 3434 is configured"
    else
        echo -e "${RED}✗${NC} Frontend port 3434 not found in docker-compose.yml"
        ERRORS=$((ERRORS + 1))
    fi
    
    if grep -q '"3232:5000"' docker-compose.yml; then
        echo -e "${GREEN}✓${NC} Backend port 3232 is configured"
    else
        echo -e "${RED}✗${NC} Backend port 3232 not found in docker-compose.yml"
        ERRORS=$((ERRORS + 1))
    fi
    
    if grep -q "host.docker.internal" docker-compose.yml; then
        echo -e "${GREEN}✓${NC} Database connection uses host.docker.internal"
    else
        echo -e "${YELLOW}⚠${NC} Database connection may not be configured for Docker"
    fi
else
    echo -e "${RED}✗${NC} docker-compose.yml not found"
    ERRORS=$((ERRORS + 1))
fi

# Check 7: Backend and Frontend directories
echo ""
echo "7. Checking application directories..."
if [ -d "backend" ]; then
    echo -e "${GREEN}✓${NC} Backend directory exists"
    if [ -f "backend/app.py" ]; then
        echo -e "${GREEN}✓${NC} Backend app.py exists"
    fi
else
    echo -e "${RED}✗${NC} Backend directory not found"
    ERRORS=$((ERRORS + 1))
fi

if [ -d "frontend" ]; then
    echo -e "${GREEN}✓${NC} Frontend directory exists"
else
    echo -e "${RED}✗${NC} Frontend directory not found"
    ERRORS=$((ERRORS + 1))
fi

# Summary
echo ""
echo "=========================================="
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed!${NC}"
    echo "=========================================="
    echo ""
    echo "Configuration Summary:"
    echo "  Frontend Port: 3434"
    echo "  Backend Port: 3232"
    echo "  Database: PostgreSQL on server (localhost:5432/monitor)"
    echo ""
    echo "Ready to deploy with:"
    echo "  ./deploy.sh"
    echo "  or"
    echo "  docker-compose up -d"
    echo ""
    exit 0
else
    echo -e "${RED}❌ Found $ERRORS error(s)${NC}"
    echo "=========================================="
    echo ""
    echo "Please fix the errors above before deploying."
    echo ""
    exit 1
fi

