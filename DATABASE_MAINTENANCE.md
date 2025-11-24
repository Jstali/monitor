# Database Maintenance Guide

## 🔍 Quick Health Check

To verify your database is properly configured, run:

```bash
cd backend
source venv/bin/activate
python verify_database_schema.py
```

This will check:
- ✅ Database connection
- ✅ All required tables exist
- ✅ Employee table has correct schema
- ✅ Organizations exist
- ✅ Passwords are properly hashed

---

## 🚨 Common Issues & Fixes

### Issue 1: "column employees.organization_id does not exist"

**Symptoms:**
- Login fails with 500 error
- Error mentions missing columns: `organization_id`, `manager_id`, or `is_active`

**Fix:**
```bash
cd backend
source venv/bin/activate
python migrate_add_organization.py
```

---

### Issue 2: "Invalid salt" or "ValueError: Invalid salt"

**Symptoms:**
- Login fails with 500 error
- Error message mentions "Invalid salt"
- Password verification fails

**Fix:**
```bash
cd backend
source venv/bin/activate
python fix_all_passwords.py
```

**Note:** This sets all passwords to `test@123`. Users should change their passwords after logging in.

---

### Issue 3: Database doesn't exist

**Symptoms:**
- Connection error: "database does not exist"
- Backend fails to start

**Fix:**
```bash
cd backend
source venv/bin/activate
python create_db.py
python migrate_add_organization.py
```

---

## 🛠️ Maintenance Scripts

### Create Database
Creates the PostgreSQL database and all tables:
```bash
python create_db.py
```

### Add Organization Support
Adds missing columns for organization/manager features:
```bash
python migrate_add_organization.py
```

### Fix Password Hashing
Converts all passwords to bcrypt format:
```bash
python fix_all_passwords.py
```

### Reset Single Password
Reset password for a specific user:
```bash
# Edit reset_password.py to set the email and password
python reset_password.py
```

### Verify Database Schema
Check if database is properly configured:
```bash
python verify_database_schema.py
```

---

## 📋 Setup Checklist for New Installation

Run these commands in order:

1. **Create virtual environment:**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Create database:**
   ```bash
   python create_db.py
   ```

4. **Run migrations:**
   ```bash
   python migrate_add_organization.py
   ```

5. **Verify setup:**
   ```bash
   python verify_database_schema.py
   ```

6. **Start backend:**
   ```bash
   python app.py
   ```

---

## 🔄 Preventing Future Issues

### Before Deploying Changes:
1. Always run `verify_database_schema.py` before starting the backend
2. Keep migration scripts in version control
3. Document any schema changes

### After Pulling Updates:
1. Check if new migration scripts exist
2. Run any new migrations
3. Verify schema with `verify_database_schema.py`

### Before Restoring Backups:
1. Note the schema version of the backup
2. Run appropriate migrations after restore
3. Verify with `verify_database_schema.py`

---

## 📊 Database Information

### Current Schema Version
- Organizations table with multi-tenancy support
- Employee table with organization_id, manager_id, is_active
- Monitoring sessions, activities, screenshots
- Monitoring configs (allowlist)

### Password Hashing
- Uses **bcrypt** for secure password storage
- Bcrypt hashes start with `$2b$` or `$2a$`
- Old SHA-256 hashes (64 hex chars) need migration

### Foreign Key Relationships
```
organizations (1) ──→ (many) employees
employees (1) ──→ (many) monitoring_sessions
employees (1) ──→ (many) employees (manager relationship)
monitoring_sessions (1) ──→ (many) activities
monitoring_sessions (1) ──→ (many) screenshots
organizations (1) ──→ (many) monitoring_configs
```

---

## 🆘 Emergency Recovery

If the database is completely broken:

1. **Backup current data** (if possible):
   ```bash
   pg_dump -U postgres monitor > backup.sql
   ```

2. **Drop and recreate:**
   ```bash
   psql -U postgres -c "DROP DATABASE monitor;"
   python create_db.py
   python migrate_add_organization.py
   ```

3. **Restore data** (if you have a backup):
   ```bash
   psql -U postgres monitor < backup.sql
   python migrate_add_organization.py
   python fix_all_passwords.py
   ```

4. **Verify:**
   ```bash
   python verify_database_schema.py
   ```

---

## 📞 Support

If you encounter issues not covered here:
1. Run `verify_database_schema.py` and check the output
2. Check backend logs for detailed error messages
3. Ensure PostgreSQL is running: `psql -U postgres -l`
4. Verify DATABASE_URL in `.env` is correct
