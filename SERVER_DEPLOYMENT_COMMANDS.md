# 🚀 Server Deployment Commands

Complete command reference for deploying the Employee Monitoring Application on a server.

---

## 📋 Quick Start (All-in-One)

```bash
# Navigate to project directory
cd /root/monitor

# Create .env file (if not exists)
cp .env.example .env

# Generate secure keys and add to .env
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env
echo "JWT_SECRET_KEY=$(openssl rand -hex 32)" >> .env
echo "DATABASE_URL=postgresql+psycopg://postgres:abcd@host.docker.internal:5432/monitor" >> .env
echo "VITE_API_URL=http://localhost:3232/api" >> .env

# Build and start services
docker-compose build
docker-compose up -d

# Wait for services to initialize
sleep 15

# Check status
docker-compose ps

# Test backend
curl http://localhost:3232/api/health
```

---

## 🔧 Step-by-Step Commands

### Step 1: Navigate to Project Directory

```bash
cd /root/monitor
```

### Step 2: Configure Environment Variables

```bash
# Create .env file from template
cp .env.example .env

# Edit .env file
nano .env
# or
vi .env
```

**Required .env Configuration:**
```env
# Database Configuration
DATABASE_URL=postgresql+psycopg://postgres:abcd@host.docker.internal:5432/monitor
POSTGRES_PASSWORD=abcd
POSTGRES_DB=monitor
POSTGRES_USER=postgres

# Application Secrets (generate secure keys)
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Frontend API URL
VITE_API_URL=http://localhost:3232/api
# For external access: VITE_API_URL=http://YOUR_SERVER_IP:3232/api

# Optional: Mistral AI
MISTRAL_API_KEY=your-mistral-api-key
OCR_ENABLED=true
```

**Generate Secure Keys:**
```bash
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env
echo "JWT_SECRET_KEY=$(openssl rand -hex 32)" >> .env
```

### Step 3: Build Docker Images

```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build backend
docker-compose build frontend
```

### Step 4: Start Services

```bash
# Start all services in detached mode
docker-compose up -d

# Start with logs visible
docker-compose up

# Start specific service
docker-compose up -d backend
docker-compose up -d frontend
```

### Step 5: Check Service Status

```bash
# Check all services
docker-compose ps

# Check specific service
docker ps | grep monitor

# Check service health
docker-compose ps --format json
```

### Step 6: View Logs

```bash
# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View specific service logs
docker-compose logs backend
docker-compose logs frontend

# View last 100 lines
docker-compose logs --tail=100

# View logs with timestamps
docker-compose logs -t
```

### Step 7: Verify Deployment

```bash
# Test backend health
curl http://localhost:3232/api/health

# Test frontend
curl http://localhost:3434

# Test from external IP (replace with your server IP)
curl http://YOUR_SERVER_IP:3232/api/health
```

---

## 🔄 Management Commands

### Start Services

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose start backend
docker-compose start frontend
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop without removing volumes
docker-compose stop

# Stop specific service
docker-compose stop backend
```

### Restart Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart backend
docker-compose restart frontend
```

### Rebuild Services

```bash
# Rebuild and restart
docker-compose up -d --build

# Rebuild specific service
docker-compose build --no-cache backend
docker-compose up -d backend
```

### Remove Services

```bash
# Stop and remove containers
docker-compose down

# Remove containers, networks, and volumes
docker-compose down -v

# Remove images
docker-compose down --rmi all
```

---

## 🔍 Monitoring Commands

### Check Resource Usage

```bash
# Container resource usage
docker stats

# Specific container
docker stats monitor_backend
docker stats monitor_frontend
```

### Check Logs

```bash
# Real-time logs
docker-compose logs -f

# Last 50 lines of backend
docker-compose logs --tail=50 backend

# Logs with timestamps
docker-compose logs -t -f
```

### Check Network

```bash
# List networks
docker network ls

# Inspect network
docker network inspect monitor_monitor_network
```

### Check Volumes

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect monitor_screenshots
```

---

## 🗄️ Database Commands

### Access Database

```bash
# Connect to PostgreSQL (if using Docker PostgreSQL)
docker-compose exec postgres psql -U postgres -d monitor

# Connect to server PostgreSQL from host
psql -h localhost -U postgres -d monitor
# Password: abcd
```

### Database Backup

```bash
# Backup database
docker-compose exec postgres pg_dump -U postgres monitor > backup_$(date +%Y%m%d).sql

# Or from host
pg_dump -h localhost -U postgres -d monitor > backup_$(date +%Y%m%d).sql
```

### Database Restore

```bash
# Restore database
docker-compose exec -T postgres psql -U postgres monitor < backup.sql

# Or from host
psql -h localhost -U postgres -d monitor < backup.sql
```

---

## 🛠️ Troubleshooting Commands

### Check Ports

```bash
# Check if ports are in use
sudo netstat -tulpn | grep -E ':(3232|3434)'

# Or using ss
sudo ss -tulpn | grep -E ':(3232|3434)'
```

### Check Container Status

```bash
# Detailed container info
docker inspect monitor_backend
docker inspect monitor_frontend

# Container logs
docker logs monitor_backend
docker logs monitor_frontend
```

### Restart Failed Container

```bash
# Restart specific container
docker restart monitor_backend
docker restart monitor_frontend

# Recreate container
docker-compose up -d --force-recreate backend
```

### Check Environment Variables

```bash
# Check environment in container
docker exec monitor_backend env | grep DATABASE
docker exec monitor_backend env | grep SECRET
```

### Test Database Connection

```bash
# Test from backend container
docker exec monitor_backend python -c "
from app import create_app
app = create_app()
with app.app_context():
    from models import db
    db.engine.connect()
    print('Database connection successful')
"
```

---

## 📊 Service Information

### Service URLs

- **Frontend**: http://localhost:3434 (or http://YOUR_SERVER_IP:3434)
- **Backend API**: http://localhost:3232/api (or http://YOUR_SERVER_IP:3232/api)
- **Health Check**: http://localhost:3232/api/health

### Port Mappings

| Service | Container Port | Host Port |
|---------|---------------|-----------|
| Frontend | 80 | 3434 |
| Backend | 5000 | 3232 |
| Database | 5432 | 5432 (server) |

### Container Names

- `monitor_backend` - Backend API container
- `monitor_frontend` - Frontend container

---

## 🔐 Security Commands

### Update Secrets

```bash
# Generate new secret keys
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)

# Update .env file
sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
sed -i "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$JWT_SECRET_KEY/" .env

# Restart services
docker-compose restart
```

### Check Firewall

```bash
# Check firewall status
sudo ufw status

# Allow ports (if using ufw)
sudo ufw allow 3232/tcp
sudo ufw allow 3434/tcp
```

---

## 📝 Complete Deployment Script

Save this as `deploy-server.sh`:

```bash
#!/bin/bash
set -e

echo "=========================================="
echo "Employee Monitoring App - Server Deployment"
echo "=========================================="

cd /root/monitor

# Create .env if not exists
if [ ! -f .env ]; then
    cp .env.example .env
    echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env
    echo "JWT_SECRET_KEY=$(openssl rand -hex 32)" >> .env
    echo "DATABASE_URL=postgresql+psycopg://postgres:abcd@host.docker.internal:5432/monitor" >> .env
    echo "VITE_API_URL=http://localhost:3232/api" >> .env
fi

# Build images
echo "Building Docker images..."
docker-compose build

# Start services
echo "Starting services..."
docker-compose up -d

# Wait for initialization
echo "Waiting for services to initialize..."
sleep 15

# Check status
echo "Service Status:"
docker-compose ps

# Test backend
echo ""
echo "Testing backend..."
curl -s http://localhost:3232/api/health && echo " ✅ Backend is healthy" || echo " ❌ Backend not responding"

echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo "Frontend: http://localhost:3434"
echo "Backend:  http://localhost:3232/api"
echo "=========================================="
```

Make it executable and run:
```bash
chmod +x deploy-server.sh
./deploy-server.sh
```

---

## 🎯 Quick Reference

| Action | Command |
|--------|---------|
| **Start** | `docker-compose up -d` |
| **Stop** | `docker-compose down` |
| **Restart** | `docker-compose restart` |
| **Logs** | `docker-compose logs -f` |
| **Status** | `docker-compose ps` |
| **Rebuild** | `docker-compose up -d --build` |
| **Health Check** | `curl http://localhost:3232/api/health` |

---

## 📞 Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Verify configuration: `cat .env`
- Test connectivity: `curl http://localhost:3232/api/health`

