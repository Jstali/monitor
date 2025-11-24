import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql+psycopg://postgres:stali@localhost:5432/monitor')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = 24 * 3600  # 24 hours
    
    # Screenshot settings
    SCREENSHOT_FOLDER = os.path.join(os.path.dirname(__file__), 'screenshots')
    MAX_SCREENSHOT_SIZE = 5 * 1024 * 1024  # 5MB
    
    # OCR/Extraction API settings (Mistral)
    MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY', 'CNYRMJHhgFHMJQQBqgKKNX6zjwXzFmQ0')
    MISTRAL_API_URL = os.getenv('MISTRAL_API_URL', 'https://api.mistral.ai/v1/chat/completions')
    OCR_ENABLED = os.getenv('OCR_ENABLED', 'true').lower() == 'true'
    OCR_TIMEOUT = int(os.getenv('OCR_TIMEOUT', '30'))
    
    # Legacy extraction API settings (deprecated, use Mistral instead)
    EXTRACTION_API_KEY = os.getenv('EXTRACTION_API_KEY', '')
    EXTRACTION_API_URL = os.getenv('EXTRACTION_API_URL', '')
    
    # Monitoring settings
    DEFAULT_SCREENSHOT_INTERVAL = 10  # seconds
    MIN_SCREENSHOT_INTERVAL = 5
    MAX_SCREENSHOT_INTERVAL = 300
