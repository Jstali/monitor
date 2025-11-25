#!/bin/bash

# Complete Deployment Script for Employee Monitoring Application
# Database Password: abc
# Backend Port: 3232
# Frontend Port: 3434

set -e

echo "==========================================="
echo "Employee Monitoring App - Deployment"
echo "==========================================="
echo ""

# Navigate to project directory
cd /root/monitor

echo "📝 Step 1: Setting up environment..."
# Copy environment template
cp .env.example .env

# Generate secure keys
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env
echo "JWT_SECRET_KEY=$(openssl rand -hex 32)" >> .env

echo "✅ Environment configured"
echo ""

echo "🔨 Step 2: Building Docker images..."
docker-compose build

echo ""
echo "🚀 Step 3: Starting services..."
docker-compose up -d

echo ""
echo "⏳ Step 4: Waiting for services to initialize..."
sleep 15

echo ""
echo "🔍 Step 5: Checking service status..."
docker-compose ps

echo ""
echo "==========================================="
echo "✅ DEPLOYMENT SUCCESSFUL!"
echo "==========================================="
echo ""
echo "📱 Access URLs:"
echo "   Frontend:    http://localhost:3434"
echo "   Backend API: http://localhost:3232/api"
echo ""
echo "📊 Database Information:"
echo "   Host:     localhost"
echo "   Port:     5432"
echo "   Database: monitor"
echo "   User:     postgres"
echo "   Password: abc"
echo ""
echo "📖 Next Steps:"
echo "   1. Open http://localhost:3434 in your browser"
echo "   2. Register an admin account"
echo "   3. Login and start using the application"
echo ""
echo "🔧 Useful Commands:"
echo "   View logs:       docker-compose logs -f"
echo "   Stop services:   docker-compose down"
echo "   Restart:         docker-compose restart"
echo "   Access DB:       docker-compose exec postgres psql -U postgres -d monitor"
echo ""
echo "==========================================="
