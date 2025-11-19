# Quick Start Guide

## 🚀 Fastest Way to Get Started

### Option 1: Automated Setup (Recommended)

```bash
cd /Users/stalin_j/monitor
./quick-start.sh
```

This will automatically:
- Set up Python virtual environments
- Install all dependencies
- Create configuration files

### Option 2: Manual Setup

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings
python app.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Agent:**
```bash
cd agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with credentials
python monitor_agent.py
```

## 🔑 Configuration

### Backend (.env)
```env
EXTRACTION_API_KEY=CNYRMJHhgFHMJQQBqgKKNX6zjwXzFmQ0
EXTRACTION_API_URL=https://your-api-endpoint.com/extract
```

### Agent (.env)
```env
API_URL=http://localhost:5000/api
EMAIL=employee@example.com
PASSWORD=your-password
```

## 📝 First Time Use

1. **Start Backend**: `cd backend && source venv/bin/activate && python app.py`
2. **Start Frontend**: `cd frontend && npm run dev`
3. **Open Browser**: Navigate to `http://localhost:5173`
4. **Register Admin**: Create an account with admin role
5. **Configure Settings**: Set screenshot interval
6. **Register Employee**: Create employee account
7. **Start Agent**: Configure and run monitoring agent

## 🎯 Testing the Application

### Test Admin Dashboard
1. Login as admin
2. View organization statistics
3. Configure screenshot interval
4. Monitor employee activity

### Test Employee Dashboard
1. Login as employee
2. Start monitoring agent
3. View personal activity
4. Check screenshots

### Test Workflow Diagrams
1. Generate session data
2. Navigate to session details
3. Click "Generate Workflow Diagram"
4. Download HTML or JSON format

## 📞 Support

For detailed documentation, see [README.md](file:///Users/stalin_j/monitor/README.md)

For complete walkthrough, see the walkthrough artifact.
