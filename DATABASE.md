# PostgreSQL Database Configuration

## ✅ Database Setup Complete

The PostgreSQL database has been successfully configured with the following details:

### Connection Details
- **Host**: localhost
- **Port**: 5432
- **Database**: monitor
- **User**: postgres
- **Password**: stali

### Created Tables
1. **organizations** - Stores organization/company information
2. **employees** - Employee accounts with authentication
3. **monitoring_sessions** - Tracking sessions with start/end times
4. **activities** - Application and website usage logs
5. **screenshots** - Screenshot metadata and extraction data

### Database URL
```
postgresql+psycopg://postgres:stali@localhost:5432/monitor
```

## 🔧 Setup Commands

### Create Database (Already Done)
```bash
cd backend
source venv/bin/activate
python create_db.py
```

### Verify Database
```bash
psql -h localhost -p 5432 -U postgres -d monitor -c "\dt"
```

This will list all tables in the database.

### Reset Database (if needed)
```bash
# Drop and recreate
psql -h localhost -p 5432 -U postgres -c "DROP DATABASE IF EXISTS monitor"
python create_db.py
```

## 📊 Database Schema

### organizations
- id (Primary Key)
- name
- screenshot_interval (seconds)
- created_at

### employees
- id (Primary Key)
- email (Unique)
- name
- password_hash
- role (admin/employee)
- organization_id (Foreign Key)
- is_active
- created_at

### monitoring_sessions
- id (Primary Key)
- employee_id (Foreign Key)
- start_time
- end_time
- is_active

### activities
- id (Primary Key)
- session_id (Foreign Key)
- timestamp
- activity_type (application/website)
- application_name
- window_title
- url
- duration_seconds

### screenshots
- id (Primary Key)
- session_id (Foreign Key)
- timestamp
- file_path
- file_size
- extracted_text
- extraction_data (JSON)
- is_processed

## 🚀 Next Steps

1. Start the Flask backend:
   ```bash
   cd backend
   source venv/bin/activate
   python app.py
   ```

2. Start the React frontend:
   ```bash
   cd frontend
   npm run dev
   ```

3. Register your first admin account at `http://localhost:5173`

## 🔍 Troubleshooting

### Connection Issues
If you get connection errors, verify PostgreSQL is running:
```bash
brew services list | grep postgresql
```

### Permission Issues
If you get permission denied errors:
```bash
psql -h localhost -p 5432 -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE monitor TO postgres"
```

### Check Tables
To verify all tables were created:
```bash
psql -h localhost -p 5432 -U postgres -d monitor -c "SELECT tablename FROM pg_tables WHERE schemaname='public'"
```
