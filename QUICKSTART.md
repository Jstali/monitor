# Quick Start Guide

## 🚀 Two Ways to Run the Application

This guide covers **both methods** for running the Employee Monitoring Application:
1. **Local Development** - Direct Python/Node.js (for development)
2. **Server/Production** - Docker Compose (for production deployment)

---

## 📍 Method 1: Local Development Setup

### Prerequisites
- Python 3.10+
- Node.js 20.19+ (or 22.12+)
- PostgreSQL 14+ installed on your machine
- npm or yarn

### Step 1: Database Setup (Required First!)

**IMPORTANT**: Set up the database BEFORE starting the backend.

```bash
# Ensure PostgreSQL is running
sudo systemctl start postgresql  # Linux
# or
brew services start postgresql  # macOS

# Create database (if not exists)
sudo -u postgres psql -c "CREATE DATABASE monitor;"

# Or connect and create:
psql -U postgres -c "CREATE DATABASE monitor;"
# Password: abcd
```

### Step 2: Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql+psycopg://postgres:abcd@localhost:5432/monitor
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)
MISTRAL_API_KEY=CNYRMJHhgFHMJQQBqgKKNX6zjwXzFmQ0
OCR_ENABLED=true
FLASK_ENV=development
EOF

# Initialize database tables
python create_db.py
python migrate_add_organization.py

# Start backend server
python app.py
```

**Backend will run on:** `http://localhost:3535`

### Step 3: Frontend Setup

```bash
# Open a new terminal
cd frontend

# Install dependencies
npm install

# Create .env file
echo "VITE_API_URL=http://localhost:3535/api" > .env

# Start development server
npm run dev
```

**Frontend will run on:** `http://localhost:3434`

### Step 4: Access the Application

1. Open browser: `http://localhost:3434`
2. Register an admin account
3. Login and start using the application

### Local Development Commands Summary

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
python app.py

# Terminal 2 - Frontend
cd frontend
npm run dev

# Terminal 3 - Agent (optional)
cd agent
source venv/bin/activate
python monitor_agent.py
```

---

## 🐳 Method 2: Server/Production Setup (Docker)

### Prerequisites
- Docker and Docker Compose installed
- PostgreSQL running on server (for connection)

### Step 1: Prepare Environment

```bash
cd /root/monitor

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    
    # Generate secure keys
    echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env
    echo "JWT_SECRET_KEY=$(openssl rand -hex 32)" >> .env
fi

# Configure database connection (server PostgreSQL)
cat >> .env << EOF
DATABASE_URL=postgresql+psycopg://postgres:abcd@host.docker.internal:5432/monitor
VITE_API_URL=http://localhost:3232/api
EOF
```

### Step 2: Deploy with Docker

**Option A: Automated Deployment (Recommended)**

```bash
chmod +x deploy.sh
./deploy.sh
```

**Option B: Manual Deployment**

```bash
# Build Docker images
docker-compose build

# Start all services
docker-compose up -d

# Wait for services to initialize
sleep 15

# Check status
docker-compose ps
```

### Step 3: Verify Deployment

```bash
# Check all containers are running
docker-compose ps

# Test backend health
curl http://localhost:3232/api/health

# View logs
docker-compose logs -f
```

### Step 4: Access the Application

- **Frontend**: `http://localhost:3434` or `http://YOUR_SERVER_IP:3434`
- **Backend API**: `http://localhost:3232/api` or `http://YOUR_SERVER_IP:3232/api`

### Docker Commands Summary

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Rebuild after code changes
docker-compose build
docker-compose up -d

# Check status
docker-compose ps
```

---

## 🔑 Configuration Reference

### Backend Configuration (.env)

**For Local Development:**
```env
DATABASE_URL=postgresql+psycopg://postgres:abcd@localhost:5432/monitor
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
MISTRAL_API_KEY=CNYRMJHhgFHMJQQBqgKKNX6zjwXzFmQ0
OCR_ENABLED=true
FLASK_ENV=development
```

**For Docker/Server:**
```env
DATABASE_URL=postgresql+psycopg://postgres:abcd@host.docker.internal:5432/monitor
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
VITE_API_URL=http://localhost:3232/api
```

### Frontend Configuration (.env)

**For Local Development:**
```env
VITE_API_URL=http://localhost:3535/api
```

**For Docker/Server:**
```env
VITE_API_URL=http://localhost:3232/api
```

### Agent Configuration (.env)

```env
API_URL=http://localhost:3535/api  # For local backend
# OR
API_URL=http://localhost:3232/api  # For Docker backend
EMAIL=employee@example.com
PASSWORD=your-password
```

---

## 📊 Port Configuration

| Service | Local Development | Docker/Server |
|---------|------------------|---------------|
| Frontend | 3434 | 3434 |
| Backend | 3535 | 3232 |
| Database | 5432 | 5432 (server) |

---

## 🗄️ Database Information

### Server PostgreSQL (Both Methods)

- **Host**: `localhost` (or server IP)
- **Port**: `5432`
- **Database**: `monitor`
- **Username**: `postgres`
- **Password**: `abcd`

### Connection Strings

**Local Development:**
```
postgresql+psycopg://postgres:abcd@localhost:5432/monitor
```

**Docker Backend:**
```
postgresql+psycopg://postgres:abcd@host.docker.internal:5432/monitor
```

---

## 🎯 Quick Start Commands

### Local Development

```bash
# 1. Setup database
psql -U postgres -c "CREATE DATABASE monitor;"

# 2. Start backend
cd backend && source venv/bin/activate && python app.py

# 3. Start frontend (new terminal)
cd frontend && npm run dev

# 4. Access: http://localhost:3434
```

### Docker/Server

```bash
# 1. Deploy
./deploy.sh

# 2. Access: http://localhost:3434 or http://YOUR_SERVER_IP:3434
```

---

## 🔧 Troubleshooting

### Local Development Issues

**Backend won't start:**
```bash
# Check if port 3535 is available
netstat -tulpn | grep 3535

# Check database connection
psql -U postgres -d monitor -c "SELECT 1;"
```

**Frontend won't start:**
```bash
# Check Node.js version (needs 20.19+)
node --version

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**CORS errors:**
- Ensure backend is running on port 3535
- Check frontend .env has correct API URL
- Hard refresh browser (Ctrl+Shift+R)

### Docker Issues

**Containers won't start:**
```bash
# Check logs
docker-compose logs

# Check if ports are in use
sudo netstat -tulpn | grep -E ':(3232|3434)'
```

**Database connection failed:**
```bash
# Verify server PostgreSQL is running
sudo systemctl status postgresql

# Test connection from Docker
docker exec monitor_backend python -c "from app import create_app; app = create_app(); print('DB connected')"
```

---

## 📝 First Time Use

1. **Start Backend** (Method 1 or 2)
2. **Start Frontend** (Method 1 or 2)
3. **Open Browser**: Navigate to `http://localhost:3434`
4. **Register Admin**: Create an account with admin role
5. **Configure Settings**: Set screenshot interval
6. **Register Employee**: Create employee account
7. **Start Agent**: Configure and run monitoring agent

---

## 📞 Support

For detailed documentation, see:
- [README.md](README.md) - Complete documentation
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment details
- [DEPLOYMENT_COMMANDS.md](DEPLOYMENT_COMMANDS.md) - Docker commands

---

## ✅ Summary

**Choose your method:**

- **Local Development**: Use when developing, testing, or running on your local machine
  - Backend: `python app.py` → Port 3535
  - Frontend: `npm run dev` → Port 3434
  - Database: Server PostgreSQL on port 5432

- **Docker/Server**: Use for production deployment or server installation
  - Backend: Docker container → Port 3232
  - Frontend: Docker container → Port 3434
  - Database: Server PostgreSQL on port 5432

Both methods connect to the same server PostgreSQL database with password `abcd`.
