from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import bcrypt
from cryptography.fernet import Fernet
import base64
import os

db = SQLAlchemy()

# Encryption key for agent credentials (use SECRET_KEY from config)
def get_encryption_key():
    """Get or generate encryption key for agent credentials"""
    secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    # Generate a 32-byte key from SECRET_KEY
    key = base64.urlsafe_b64encode(secret_key[:32].encode().ljust(32, b'0')[:32])
    return key

def encrypt_credentials(email, password):
    """Encrypt agent credentials"""
    key = get_encryption_key()
    f = Fernet(key)
    combined = f"{email}:{password}".encode()
    encrypted = f.encrypt(combined)
    return encrypted.decode()

def decrypt_credentials(encrypted_data):
    """Decrypt agent credentials"""
    try:
        key = get_encryption_key()
        f = Fernet(key)
        decrypted = f.decrypt(encrypted_data.encode())
        email, password = decrypted.decode().split(':', 1)
        return email, password
    except Exception as e:
        raise ValueError(f"Failed to decrypt credentials: {str(e)}")

class Organization(db.Model):
    """Organization model"""
    __tablename__ = 'organizations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    screenshot_interval = db.Column(db.Integer, default=10)  # seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    employees = db.relationship('Employee', backref='organization', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'screenshot_interval': self.screenshot_interval,
            'created_at': self.created_at.isoformat(),
            'employee_count': len(self.employees)
        }


class Employee(db.Model):
    """Employee model"""
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='employee')  # 'super_admin', 'admin' (manager), or 'employee'
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)  # Manager assignment
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Encrypted agent credentials (stored when employee provides them via dashboard)
    agent_credentials_encrypted = db.Column(db.Text, nullable=True)
    
    # Relationships
    sessions = db.relationship('MonitoringSession', backref='employee', lazy=True, cascade='all, delete-orphan')
    managed_employees = db.relationship('Employee', backref=db.backref('manager', remote_side=[id]), lazy=True)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Check if password matches"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self, include_sessions=False):
        data = {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'organization_id': self.organization_id,
            'manager_id': self.manager_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }
        if include_sessions:
            data['sessions'] = [s.to_dict() for s in self.sessions]
        return data


class MonitoringSession(db.Model):
    """Monitoring session model - tracks a period of monitoring"""
    __tablename__ = 'monitoring_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    activities = db.relationship('Activity', backref='session', lazy=True, cascade='all, delete-orphan')
    screenshots = db.relationship('Screenshot', backref='session', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_details=False):
        data = {
            'id': self.id,
            'employee_id': self.employee_id,
            'start_time': self.start_time.isoformat() + 'Z' if self.start_time else None,
            'end_time': self.end_time.isoformat() + 'Z' if self.end_time else None,
            'is_active': self.is_active,
            'duration_seconds': (self.end_time - self.start_time).total_seconds() if self.end_time else None
        }
        if include_details:
            data['activities'] = [a.to_dict() for a in self.activities]
            data['screenshots'] = [s.to_dict() for s in self.screenshots]
        return data


class Activity(db.Model):
    """Activity tracking - applications and websites"""
    __tablename__ = 'activities'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('monitoring_sessions.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    activity_type = db.Column(db.String(50))  # 'application' or 'website'
    application_name = db.Column(db.String(200), nullable=True)
    window_title = db.Column(db.String(500), nullable=True)
    url = db.Column(db.String(1000), nullable=True)
    duration_seconds = db.Column(db.Integer, default=0)
    in_allowlist = db.Column(db.Boolean, default=False)  # Track if activity was in allowlist
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'timestamp': self.timestamp.isoformat() + 'Z' if self.timestamp else None,
            'activity_type': self.activity_type,
            'application_name': self.application_name,
            'window_title': self.window_title,
            'url': self.url,
            'duration_seconds': self.duration_seconds,
            'in_allowlist': self.in_allowlist
        }


class Screenshot(db.Model):
    """Screenshot model"""
    __tablename__ = 'screenshots'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('monitoring_sessions.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    extracted_text = db.Column(db.Text, nullable=True)
    extraction_data = db.Column(db.JSON, nullable=True)  # Store full extraction response
    is_processed = db.Column(db.Boolean, default=False)
    folder_name = db.Column(db.String(100), nullable=True)  # Dynamic folder based on allowlist
    activity_name = db.Column(db.String(200), nullable=True)  # Activity label for process mining
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'timestamp': self.timestamp.isoformat() + 'Z' if self.timestamp else None,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'extracted_text': self.extracted_text,
            'extraction_data': self.extraction_data,
            'is_processed': self.is_processed,
            'folder_name': self.folder_name,
            'activity_name': self.activity_name
        }


class MonitoringConfig(db.Model):
    """Manager-configured allowlist for selective monitoring"""
    __tablename__ = 'monitoring_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    config_type = db.Column(db.String(20), nullable=False)  # 'application' or 'url'
    pattern = db.Column(db.String(500), nullable=False)  # App name or URL domain
    folder_name = db.Column(db.String(100), nullable=False)  # Dynamic folder name
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'config_type': self.config_type,
            'pattern': self.pattern,
            'folder_name': self.folder_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }
