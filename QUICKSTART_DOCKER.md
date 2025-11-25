# 🚀 Quick Start - Database & Docker Deployment

## Step 1: Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Generate secure keys (run these commands)
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env
echo "JWT_SECRET_KEY=$(openssl rand -hex 32)" >> .env
```

## Step 2: Deploy with Docker

### Option A: Automated Deployment (Recommended)

```bash
./deploy.sh
```

### Option B: Manual Deployment

```bash
# Build and start all services
docker-compose up -d

# Check service status
docker-compose ps
```

## Step 3: Access the Application

- **Frontend**: http://your-server-ip (or http://localhost)
- **Backend API**: http://your-server-ip:5000/api

## Step 4: Create Admin Account

1. Open the frontend in your browser
2. Click "Register"
3. Fill in details and select "Admin" role
4. Login with your credentials

## Database Access

### Connect to PostgreSQL

```bash
# Using Docker
docker-compose exec postgres psql -U postgres -d monitor

# From host (if PostgreSQL client installed)
psql -h localhost -p 5432 -U postgres -d monitor
# Password: abc
```

### Database Details

- **Host**: localhost (or postgres from within Docker network)
- **Port**: 5432
- **Database**: monitor
- **User**: postgres
- **Password**: abc

## Common Commands

```bash
# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# Backup database
docker-compose exec postgres pg_dump -U postgres monitor > backup.sql

# Restore database
docker-compose exec -T postgres psql -U postgres monitor < backup.sql
```

## Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs

# Check if ports are in use
sudo netstat -tulpn | grep -E ':(80|5000|5432)'
```

### Database connection failed
```bash
# Check PostgreSQL health
docker-compose ps postgres

# View database logs
docker-compose logs postgres
```

### Permission denied
```bash
# Fix permissions
sudo chown -R $USER:$USER .
```

## What's Running?

After deployment, you'll have:

1. **PostgreSQL Database** (port 5432)
   - Stores all application data
   - Persistent volume for data retention

2. **Flask Backend** (port 5000)
   - REST API for the application
   - Connects to PostgreSQL
   - Handles authentication and monitoring

3. **React Frontend** (port 80)
   - Web interface served by Nginx
   - Communicates with backend API

## Next Steps

1. ✅ Register admin account
2. ✅ Configure organization settings
3. ✅ Register employee accounts
4. ✅ Install monitoring agent on employee machines
5. ✅ Start monitoring sessions

For detailed information, see [DEPLOYMENT.md](file:///root/monitor/DEPLOYMENT.md)
