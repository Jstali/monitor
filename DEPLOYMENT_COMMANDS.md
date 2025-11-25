# 🚀 Complete Docker Deployment Commands

This guide provides **all the commands** you need to deploy the Employee Monitoring Application using Docker with PostgreSQL database.

## Configuration Summary

- **Backend Port**: 3232
- **Frontend Port**: 3434
- **PostgreSQL Port**: 5432
- **Database**: PostgreSQL (created automatically inside Docker)

---

## Step 1: Prepare Environment File

```bash
# Navigate to project directory
cd /root/monitor

# Copy environment template
cp .env.example .env

# Generate secure keys and add them to .env
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env
echo "JWT_SECRET_KEY=$(openssl rand -hex 32)" >> .env
```

**Optional**: Update the API URL in `.env` if deploying to a remote server:
```bash
# For remote server, replace localhost with your server IP
echo "VITE_API_URL=http://YOUR_SERVER_IP:3232/api" >> .env
```

---

## Step 2: Deploy with Docker

### Option A: Automated Deployment (Recommended)

```bash
# Make deploy script executable
chmod +x deploy.sh

# Run deployment script
./deploy.sh
```

### Option B: Manual Deployment

```bash
# Build all Docker images
docker-compose build

# Start all services in detached mode
docker-compose up -d

# Wait for services to initialize (about 10-15 seconds)
sleep 15

# Check service status
docker-compose ps
```

---

## Step 3: Verify Deployment

```bash
# Check if all containers are running
docker-compose ps

# View logs from all services
docker-compose logs

# View logs from specific service
docker-compose logs postgres
docker-compose logs backend
docker-compose logs frontend

# Follow logs in real-time
docker-compose logs -f
```

---

## Step 4: Access the Application

### Web Interface
- **Frontend**: `http://localhost:3434` (or `http://YOUR_SERVER_IP:3434`)
- **Backend API**: `http://localhost:3232/api` (or `http://YOUR_SERVER_IP:3232/api`)

### Test Backend API
```bash
# Check backend health
curl http://localhost:3232/api/health

# Or from remote server
curl http://YOUR_SERVER_IP:3232/api/health
```

---

## Step 5: Create Admin Account

1. Open your browser and navigate to: `http://localhost:3434` (or your server IP)
2. Click **"Register"**
3. Fill in the registration form:
   - Username
   - Email
   - Password
   - Select **"Admin"** role
4. Click **"Register"**
5. Login with your credentials

---

## Database Information

The PostgreSQL database is **automatically created** inside the Docker container.

### Connection Details

- **Host**: `localhost` (from host machine) or `postgres` (from within Docker network)
- **Port**: `5432`
- **Database Name**: `monitor`
- **Username**: `postgres`
- **Password**: `abc`

### Access Database

```bash
# Connect to PostgreSQL using Docker
docker-compose exec postgres psql -U postgres -d monitor

# Once connected, you can run SQL commands:
# \dt              - List all tables
# \d table_name    - Describe table structure
# SELECT * FROM users;  - Query users table
# \q               - Quit
```

### Database from Host Machine

If you have PostgreSQL client installed on your host:
```bash
psql -h localhost -p 5432 -U postgres -d monitor
# Password: abc
```

---

## Common Management Commands

### View Service Status
```bash
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Restart Services
```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart backend
docker-compose restart frontend
docker-compose restart postgres
```

### Stop Services
```bash
# Stop all services (keeps data)
docker-compose stop

# Stop and remove containers (keeps data volumes)
docker-compose down

# Stop and remove everything including volumes (⚠️ DELETES DATABASE)
docker-compose down -v
```

### Rebuild After Code Changes
```bash
# Rebuild and restart all services
docker-compose up -d --build

# Rebuild specific service
docker-compose up -d --build backend
docker-compose up -d --build frontend
```

---

## Database Backup & Restore

### Backup Database
```bash
# Create backup file
docker-compose exec postgres pg_dump -U postgres monitor > backup_$(date +%Y%m%d_%H%M%S).sql

# Or with specific filename
docker-compose exec postgres pg_dump -U postgres monitor > monitor_backup.sql
```

### Restore Database
```bash
# Restore from backup
docker-compose exec -T postgres psql -U postgres monitor < monitor_backup.sql
```

---

## Troubleshooting

### Check if Ports are Available
```bash
# Check if ports 3434, 3232, 5432 are in use
sudo netstat -tulpn | grep -E ':(3434|3232|5432)'

# Or using ss command
sudo ss -tulpn | grep -E ':(3434|3232|5432)'
```

### Services Won't Start
```bash
# Check detailed logs
docker-compose logs

# Check specific service
docker-compose logs postgres
docker-compose logs backend

# Restart services
docker-compose restart
```

### Database Connection Failed
```bash
# Check PostgreSQL container status
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Verify database is ready
docker-compose exec postgres pg_isready -U postgres -d monitor
```

### Permission Issues
```bash
# Fix file permissions
sudo chown -R $USER:$USER /root/monitor

# Fix Docker socket permissions (if needed)
sudo chmod 666 /var/run/docker.sock
```

### Clear Everything and Start Fresh
```bash
# Stop and remove all containers and volumes
docker-compose down -v

# Remove all images
docker-compose down --rmi all

# Start fresh deployment
docker-compose up -d --build
```

---

## Complete Deployment Script (All-in-One)

Copy and paste this entire script to deploy everything:

```bash
#!/bin/bash

# Navigate to project directory
cd /root/monitor

# Setup environment
cp .env.example .env
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env
echo "JWT_SECRET_KEY=$(openssl rand -hex 32)" >> .env

# Build and deploy
docker-compose build
docker-compose up -d

# Wait for services
echo "Waiting for services to start..."
sleep 15

# Check status
echo "==================================="
echo "Deployment Status:"
echo "==================================="
docker-compose ps

echo ""
echo "==================================="
echo "Access URLs:"
echo "==================================="
echo "Frontend: http://localhost:3434"
echo "Backend API: http://localhost:3232/api"
echo ""
echo "Database: localhost:5432"
echo "Database Name: monitor"
echo "Username: postgres"
echo "Password: stali"
echo "==================================="
```

Save this as `quick-deploy.sh`, make it executable, and run:
```bash
chmod +x quick-deploy.sh
./quick-deploy.sh
```

---

## What Gets Deployed?

After successful deployment, you'll have:

1. **PostgreSQL Database Container** (`monitor_postgres`)
   - Port: 5432
   - Database automatically created and initialized
   - Persistent data storage

2. **Backend API Container** (`monitor_backend`)
   - Port: 3232
   - Flask REST API
   - Connected to PostgreSQL

3. **Frontend Container** (`monitor_frontend`)
   - Port: 3434
   - React application served by Nginx
   - Configured to connect to backend at port 3232

---

## Next Steps After Deployment

1. ✅ Access frontend at `http://localhost:3434`
2. ✅ Register admin account
3. ✅ Login to admin dashboard
4. ✅ Configure organization settings
5. ✅ Register employee accounts
6. ✅ Install monitoring agent on employee machines
7. ✅ Start monitoring sessions

---

## Quick Reference

| Service | Port | URL |
|---------|------|-----|
| Frontend | 3434 | http://localhost:3434 |
| Backend | 3232 | http://localhost:3232/api |
| PostgreSQL | 5432 | localhost:5432 |

**Database Credentials:**
- User: `postgres`
- Password: `abcd`
- Database: `monitor`
