#!/bin/bash

# Quick deployment script for Employee Monitoring Application
# This script helps you quickly deploy the application with Docker

set -e

echo "=========================================="
echo "Employee Monitoring App - Quick Deploy"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed!"
    echo "Please install Docker first:"
    echo "  curl -fsSL https://get.docker.com -o get-docker.sh"
    echo "  sudo sh get-docker.sh"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed!"
    echo "Please install Docker Compose first:"
    echo "  sudo apt-get install docker-compose-plugin"
    exit 1
fi

echo "✅ Docker is installed"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  IMPORTANT: Please edit .env file and set your SECRET_KEY and JWT_SECRET_KEY"
    echo "   You can generate random keys with: openssl rand -hex 32"
    echo ""
    read -p "Press Enter to continue after editing .env file..."
fi

echo "🔨 Building Docker images..."
docker-compose build

echo ""
echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "=========================================="
    echo "✅ Deployment Successful!"
    echo "=========================================="
    echo ""
    echo "Services are running:"
    docker-compose ps
    echo ""
    echo "📱 Access the application:"
    echo "   Frontend: http://localhost:3434"
    echo "   Backend API: http://localhost:3232/api"
    echo ""
    echo "📊 Database Information:"
    echo "   Host: localhost (server PostgreSQL)"
    echo "   Port: 5432"
    echo "   Database: monitor"
    echo "   User: postgres"
    echo "   Password: abcd"
    echo ""
    echo "📖 Next Steps:"
    echo "   1. Open http://localhost:3434 in your browser"
    echo "   2. Register an admin account"
    echo "   3. Login and start using the application"
    echo ""
    echo "🔧 Useful Commands:"
    echo "   View logs: docker-compose logs -f"
    echo "   Stop services: docker-compose down"
    echo "   Restart services: docker-compose restart"
    echo ""
else
    echo ""
    echo "❌ Deployment failed!"
    echo "Check logs with: docker-compose logs"
    exit 1
fi
