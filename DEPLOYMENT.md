# Docker Deployment Guide

This guide will help you deploy the Employee Monitoring Application using Docker and Docker Compose on your server.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 2GB free disk space
- Ports 80, 5000, and 5432 available

## Quick Start

### 1. Install Docker (if not already installed)

```bash
# Update package index
sudo apt-get update

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group (optional, to run without sudo)
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo apt-get install docker-compose-plugin
```

### 2. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your settings
nano .env
```

**Important:** Change these values in `.env`:
- `SECRET_KEY` - Use a strong random string
- `JWT_SECRET_KEY` - Use a different strong random string
- `MISTRAL_API_KEY` - Your Mistral API key (if using OCR features)

### 3. Start the Application

```bash
# Build and start all services
docker-compose up -d

# Check if all services are running
docker-compose ps
```

You should see three services running:
- `monitor_postgres` - PostgreSQL database
- `monitor_backend` - Flask API
- `monitor_frontend` - React frontend with Nginx

### 4. Access the Application

Open your browser and navigate to:
- **Frontend**: http://your-server-ip
- **API**: http://your-server-ip:5000/api

### 5. Create Your First Admin Account

1. Open the frontend in your browser
2. Click "Register"
3. Fill in the registration form:
   - Email
   - Name
   - Organization Name
   - Password
   - Select "Admin" role
4. Click "Register"
5. Login with your credentials

## Database Management

### Access PostgreSQL Database

```bash
# Connect to PostgreSQL container
docker-compose exec postgres psql -U postgres -d monitor

# List all tables
\dt

# Exit PostgreSQL
\q
```

### View Database Logs

```bash
docker-compose logs postgres
```

### Backup Database

```bash
# Create a backup
docker-compose exec postgres pg_dump -U postgres monitor > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
docker-compose exec -T postgres psql -U postgres monitor < backup_20231124_120000.sql
```

### Reset Database

```bash
# Stop all services
docker-compose down

# Remove database volume (WARNING: This deletes all data!)
docker volume rm monitor_postgres_data

# Start services again (database will be recreated)
docker-compose up -d
```

## Service Management

### View Logs

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres

# Follow logs in real-time
docker-compose logs -f backend
```

### Restart Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### Stop Services

```bash
# Stop all services (keeps data)
docker-compose down

# Stop and remove volumes (WARNING: Deletes all data!)
docker-compose down -v
```

### Update Application

```bash
# Pull latest code changes
git pull

# Rebuild and restart services
docker-compose up -d --build
```

## Troubleshooting

### Services Won't Start

1. Check if ports are already in use:
```bash
sudo netstat -tulpn | grep -E ':(80|5000|5432)'
```

2. Check Docker logs:
```bash
docker-compose logs
```

### Database Connection Issues

1. Verify PostgreSQL is healthy:
```bash
docker-compose ps postgres
```

2. Check database logs:
```bash
docker-compose logs postgres
```

3. Test connection from backend:
```bash
docker-compose exec backend python -c "from app import db; print('Connected!' if db else 'Failed')"
```

### Frontend Can't Connect to Backend

1. Check if backend is running:
```bash
docker-compose ps backend
curl http://localhost:5000/api/health
```

2. Verify environment variables:
```bash
docker-compose exec frontend env | grep VITE_API_URL
```

### Permission Denied Errors

```bash
# Fix screenshot directory permissions
sudo chown -R 1000:1000 backend/screenshots

# Or run with sudo
sudo docker-compose up -d
```

## Production Considerations

### Security

1. **Change Default Credentials**: Update database password in docker-compose.yml
2. **Use Strong Keys**: Generate secure SECRET_KEY and JWT_SECRET_KEY
3. **Enable HTTPS**: Use a reverse proxy like Nginx or Traefik with SSL certificates
4. **Firewall**: Only expose necessary ports (80, 443)
5. **Regular Updates**: Keep Docker images and application code updated

### Performance

1. **Resource Limits**: Add resource limits to docker-compose.yml:
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
```

2. **Database Tuning**: Adjust PostgreSQL settings for your workload
3. **Monitoring**: Set up monitoring with Prometheus/Grafana

### Backup Strategy

1. **Automated Backups**: Set up cron job for daily database backups
```bash
# Add to crontab
0 2 * * * cd /path/to/monitor && docker-compose exec postgres pg_dump -U postgres monitor > /backups/monitor_$(date +\%Y\%m\%d).sql
```

2. **Screenshot Backups**: Backup the screenshots volume regularly
```bash
docker run --rm -v monitor_screenshots:/data -v /backups:/backup alpine tar czf /backup/screenshots_$(date +%Y%m%d).tar.gz /data
```

## Monitoring

### Check Service Health

```bash
# Check all services
docker-compose ps

# Check resource usage
docker stats
```

### Database Size

```bash
docker-compose exec postgres psql -U postgres -d monitor -c "SELECT pg_size_pretty(pg_database_size('monitor'));"
```

## Advanced Configuration

### Custom Port Mapping

Edit `docker-compose.yml` to change ports:
```yaml
services:
  frontend:
    ports:
      - "8080:80"  # Change frontend port to 8080
```

### External Database

To use an external PostgreSQL server instead of Docker:

1. Remove the `postgres` service from docker-compose.yml
2. Update `DATABASE_URL` in `.env`:
```env
DATABASE_URL=postgresql+psycopg://user:password@external-host:5432/monitor
```

### Environment-Specific Configuration

Create different environment files:
- `.env.development`
- `.env.production`

Load specific environment:
```bash
docker-compose --env-file .env.production up -d
```

## Support

For issues or questions:
1. Check logs: `docker-compose logs`
2. Verify configuration: `docker-compose config`
3. Review this documentation
4. Check application README.md
