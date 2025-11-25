from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from models import db
import os

def create_app(config_class=Config):
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Disable strict slashes to prevent 308 redirects that break CORS
    app.url_map.strict_slashes = False
    
    # Initialize extensions
    # Configure CORS to allow all origins and methods
    CORS(app, 
         origins=["*"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
         allow_headers=["Content-Type", "Authorization"],
         supports_credentials=False,
         max_age=3600)
    db.init_app(app)
    JWTManager(app)
    
    # Create screenshot folder
    os.makedirs(app.config['SCREENSHOT_FOLDER'], exist_ok=True)
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.organizations import org_bp
    from routes.employees import emp_bp
    from routes.monitoring import monitor_bp
    from routes.screenshots import screenshot_bp
    from routes.workflow import workflow_bp
    from routes.monitoring_config import config_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(org_bp, url_prefix='/api/organizations')
    app.register_blueprint(emp_bp, url_prefix='/api/employees')
    app.register_blueprint(monitor_bp, url_prefix='/api/monitoring')
    app.register_blueprint(screenshot_bp, url_prefix='/api/screenshots')
    app.register_blueprint(workflow_bp, url_prefix='/api/workflow')
    app.register_blueprint(config_bp, url_prefix='/api/monitoring-config')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    # Health check
    @app.route('/api/health')
    def health():
        return jsonify({'status': 'healthy'})
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app

# Create app instance for gunicorn
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3535)
