# Employee Monitoring Application

A comprehensive employee monitoring system with organization and employee dashboards for tracking productivity, applications, websites, and screenshots.

## 🏗️ Architecture

- **Backend**: Python Flask REST API with SQLAlchemy
- **Frontend**: React.js with Vite
- **Agent**: Python desktop monitoring agent
- **Database**: PostgreSQL 15+

## 📋 Features

### Organization Dashboard (Admin)
- Employee management
- Real-time monitoring sessions
- Screenshot gallery with extraction
- Activity tracking and analytics
- Configurable screenshot intervals
- Data visualization with charts

### Employee Dashboard
- Personal session history
- Activity timeline
- Screenshot access
- Productivity insights

### Monitoring Agent
- Cross-platform (macOS, Windows, Linux)
- Automatic screenshot capture
- Application tracking
- Website tracking
- Configurable intervals

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run the server
python app.py
```

The backend will run on `http://localhost:5000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will run on `http://localhost:5173`

### Agent Setup

```bash
cd agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with employee credentials

# Run the agent
python monitor_agent.py
```

## 📝 Configuration

### Backend (.env)
```env
DATABASE_URL=postgresql+psycopg://postgres:stali@localhost:5432/monitor
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
EXTRACTION_API_KEY=CNYRMJHhgFHMJQQBqgKKNX6zjwXzFmQ0
EXTRACTION_API_URL=https://api.example.com/extract
```

**Database Configuration:**
- Host: localhost
- Port: 5432
- Database: monitor
- User: postgres
- Password: stali

### Frontend (.env)
```env
VITE_API_URL=http://localhost:5000/api
```

### Agent (.env)
```env
API_URL=http://localhost:5000/api
EMAIL=employee@example.com
PASSWORD=your-password
```

## 🔐 First Time Setup

1. **Create the database**
   ```bash
   cd backend
   source venv/bin/activate
   python create_db.py
   ```

2. **Start the backend server**
   ```bash
   cd backend
   python app.py
   ```

3. **Register an admin account**
   - Open `http://localhost:5173` in your browser
   - Click "Register"
   - Fill in details and select "Admin" role
   - Submit registration

3. **Login and configure**
   - Login with admin credentials
   - Set screenshot interval in Settings
   - View organization dashboard

4. **Register employees**
   - Employees can register with the same organization name
   - Or admin can create accounts via API

5. **Start monitoring agent on employee machines**
   - Install agent on employee laptops
   - Configure with employee credentials
   - Run `python monitor_agent.py`

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new employee
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user

### Organizations
- `GET /api/organizations/:id` - Get organization details
- `PUT /api/organizations/:id` - Update settings
- `GET /api/organizations/:id/employees` - Get employees

### Monitoring
- `POST /api/monitoring/sessions/start` - Start session
- `POST /api/monitoring/sessions/stop` - Stop session
- `GET /api/monitoring/sessions` - Get sessions
- `POST /api/monitoring/activities` - Log activity
- `GET /api/monitoring/activities` - Get activities

### Screenshots
- `POST /api/screenshots/upload` - Upload screenshot
- `GET /api/screenshots/:id` - Get screenshot details
- `GET /api/screenshots/:id/file` - Download screenshot
- `POST /api/screenshots/:id/extract` - Extract data
- `GET /api/screenshots/session/:id` - Get session screenshots

## 🔧 Development

### Backend Development
```bash
cd backend
source venv/bin/activate
python app.py
```

### Frontend Development
```bash
cd frontend
npm run dev
```

### Building for Production

**Frontend:**
```bash
cd frontend
npm run build
```

**Backend:**
Use a production WSGI server like Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🎨 Technology Stack

### Backend
- Flask - Web framework
- Flask-SQLAlchemy - ORM
- Flask-JWT-Extended - Authentication
- Flask-CORS - CORS handling
- psutil - Process monitoring
- mss - Screenshot capture
- Pillow - Image processing

### Frontend
- React - UI framework
- Vite - Build tool
- React Router - Routing
- Axios - HTTP client
- Recharts - Data visualization
- Lucide React - Icons

### Agent
- psutil - Process tracking
- mss - Screenshot capture
- requests - API communication

## 📱 Platform Support

### Agent Compatibility
- ✅ macOS (AppleScript for window tracking)
- ✅ Windows (pygetwindow for window tracking)
- ✅ Linux (xdotool for window tracking)

## 🔒 Security Considerations

- All API endpoints require JWT authentication
- Role-based access control (Admin/Employee)
- Employees can only view their own data
- Admins can only view data within their organization
- Passwords are hashed with bcrypt
- Screenshots stored securely on server

## 📄 License

This project is for educational and internal use only.

## 🤝 Support

For issues or questions, please contact your system administrator.

## 🔄 Workflow Diagram Generation

The system supports extracting data from screenshots using the configured extraction API. To generate workflow diagrams:

1. Capture screenshots during monitoring sessions
2. Admin can trigger extraction via "Extract" button
3. Extracted text and data are stored with screenshots
4. Use the extraction data to generate workflow diagrams showing employee activity patterns

### Extraction API Integration

Configure your extraction API in backend `.env`:
```env
EXTRACTION_API_KEY=your-api-key
EXTRACTION_API_URL=https://your-extraction-api.com/extract
```

The API should accept image files and return JSON with extracted text and structured data.

## 📈 Future Enhancements

- Real-time dashboard updates with WebSockets
- Advanced analytics and reporting
- Email notifications
- Mobile app for monitoring
- AI-powered productivity insights
- Workflow diagram auto-generation from screenshots
- Video recording capabilities
- Idle time detection
- Application usage reports
