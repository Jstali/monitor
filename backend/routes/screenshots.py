from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Employee, MonitoringSession, Screenshot, Activity
from werkzeug.utils import secure_filename
import os
import requests
from datetime import datetime, timedelta

screenshot_bp = Blueprint('screenshots', __name__)

@screenshot_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_screenshot():
    """Upload a screenshot"""
    employee_id = int(get_jwt_identity())
    
    # Get active session
    active_session = MonitoringSession.query.filter_by(
        employee_id=employee_id,
        is_active=True
    ).first()
    
    if not active_session:
        return jsonify({'error': 'No active session'}), 400
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Generate unique filename
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    filename = secure_filename(f"screenshot_{employee_id}_{active_session.id}_{timestamp}.png")
    
    # Save file
    filepath = os.path.join(current_app.config['SCREENSHOT_FOLDER'], filename)
    file.save(filepath)
    
    file_size = os.path.getsize(filepath)
    
    # Create screenshot record
    screenshot = Screenshot(
        session_id=active_session.id,
        file_path=filepath,
        file_size=file_size
    )
    
    db.session.add(screenshot)
    db.session.commit()
    
    return jsonify({
        'message': 'Screenshot uploaded successfully',
        'screenshot': screenshot.to_dict()
    }), 201


@screenshot_bp.route('/<int:screenshot_id>', methods=['GET'])
@jwt_required()
def get_screenshot(screenshot_id):
    """Get screenshot details"""
    employee_id = int(get_jwt_identity())
    employee = Employee.query.get(employee_id)
    
    screenshot = Screenshot.query.get(screenshot_id)
    if not screenshot:
        return jsonify({'error': 'Screenshot not found'}), 404
    
    # Check access
    session = MonitoringSession.query.get(screenshot.session_id)
    if employee.role != 'admin' and session.employee_id != employee_id:
        return jsonify({'error': 'Access denied'}), 403
    
    if employee.role == 'admin':
        session_employee = Employee.query.get(session.employee_id)
        if session_employee.organization_id != employee.organization_id:
            return jsonify({'error': 'Access denied'}), 403
    
    return jsonify(screenshot.to_dict()), 200


@screenshot_bp.route('/<int:screenshot_id>/file', methods=['GET'])
def download_screenshot(screenshot_id):
    """Download screenshot file"""
    # Custom auth to handle query param token
    from flask_jwt_extended import verify_jwt_in_request, get_jwt
    
    try:
        # Try standard header auth first
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        
        # If not found, check query param
        if not identity:
            token = request.args.get('token')
            if token:
                # Manually decode/verify if needed, or use a helper. 
                # For simplicity with flask-jwt-extended, we can inject it into headers temporarily
                # or decode it manually.
                from flask_jwt_extended import decode_token
                decoded = decode_token(token)
                identity = decoded['sub']
            else:
                return jsonify({'error': 'Missing authorization'}), 401
                
        employee_id = int(identity)
        employee = Employee.query.get(employee_id)
        
        screenshot = Screenshot.query.get(screenshot_id)
        if not screenshot:
            return jsonify({'error': 'Screenshot not found'}), 404
        
        # Check access
        session = MonitoringSession.query.get(screenshot.session_id)
        if employee.role != 'admin' and session.employee_id != employee_id:
            return jsonify({'error': 'Access denied'}), 403
        
        if employee.role == 'admin':
            session_employee = Employee.query.get(session.employee_id)
            if session_employee.organization_id != employee.organization_id:
                return jsonify({'error': 'Access denied'}), 403
        
        if not os.path.exists(screenshot.file_path):
            return jsonify({'error': 'Screenshot file not found'}), 404
        
        return send_file(screenshot.file_path, mimetype='image/png')
        
    except Exception as e:
        return jsonify({'error': f'Authorization failed: {str(e)}'}), 401


@screenshot_bp.route('/<int:screenshot_id>/extract', methods=['POST'])
@jwt_required()
def extract_screenshot_data(screenshot_id):
    """Extract data from screenshot using external API"""
    employee_id = int(get_jwt_identity())
    employee = Employee.query.get(employee_id)
    
    # Allow admin or the employee who owns the screenshot
    # (We check ownership after fetching the screenshot)
    
    screenshot = Screenshot.query.get(screenshot_id)
    if not screenshot:
        return jsonify({'error': 'Screenshot not found'}), 404
        
    # Check access
    session = MonitoringSession.query.get(screenshot.session_id)
    if employee.role != 'admin' and session.employee_id != employee_id:
        return jsonify({'error': 'Access denied'}), 403
    
    if employee.role == 'admin':
        session_employee = Employee.query.get(session.employee_id)
        if session_employee.organization_id != employee.organization_id:
            return jsonify({'error': 'Access denied'}), 403
    
    # Check if already processed
    if screenshot.is_processed:
        return jsonify({
            'message': 'Screenshot already processed',
            'screenshot': screenshot.to_dict()
        }), 200
    
    # Check if file exists
    if not os.path.exists(screenshot.file_path):
        return jsonify({'error': 'Screenshot file not found'}), 404
    
    # Call extraction API
    api_key = current_app.config.get('EXTRACTION_API_KEY')
    api_url = current_app.config.get('EXTRACTION_API_URL')
    
    # MOCK IMPLEMENTATION if URL is placeholder
    if not api_url or 'api.example.com' in api_url:
        # Use real activity data instead of fake cycling data
        import time
        time.sleep(0.5)
        
        # Get the screenshot's session and find nearby activities
        session_id = screenshot.session_id
        screenshot_time = screenshot.timestamp
        
        # Find activities within 30 seconds of this screenshot
        time_window_start = screenshot_time - timedelta(seconds=30)
        time_window_end = screenshot_time + timedelta(seconds=30)
        
        nearby_activities = Activity.query.filter(
            Activity.session_id == session_id,
            Activity.timestamp >= time_window_start,
            Activity.timestamp <= time_window_end
        ).order_by(Activity.timestamp.desc()).first()
        
        if nearby_activities:
            # Use real activity data
            app = nearby_activities.application_name or 'Unknown'
            
            # Determine action based on activity type
            if nearby_activities.activity_type == 'website':
                action = 'Browsing'
                context = nearby_activities.url or nearby_activities.window_title or 'Web'
            else:
                action = 'Working'
                context = nearby_activities.window_title or 'Application'
            
            mock_data = {
                'app': app,
                'action': action,
                'context': context[:50] if context else '',
                'details': f"User was {action.lower()} in {app}",
                'confidence': 0.90,
                'mock': True,
                'source': 'activity_log'
            }
            mock_text = f"App: {app}\\nAction: {action}\\nContext: {context}"
        else:
            # Fallback to generic data if no activities found
            mock_data = {
                'app': 'Unknown Application',
                'action': 'Active',
                'context': 'No activity data',
                'details': 'Screenshot captured but no activity logged',
                'confidence': 0.50,
                'mock': True,
                'source': 'fallback'
            }
            mock_text = "No activity data available for this screenshot"
        
        screenshot.extracted_text = mock_text
        screenshot.extraction_data = mock_data
        screenshot.is_processed = True
        
        db.session.commit()
        
        return jsonify({
            'message': 'Screenshot data extracted successfully (Mock)',
            'screenshot': screenshot.to_dict()
        }), 200

    if not api_key or not api_url:
        return jsonify({'error': 'Extraction API not configured'}), 500
    
    try:
        with open(screenshot.file_path, 'rb') as f:
            files = {'file': f}
            headers = {'Authorization': f'Bearer {api_key}'}
            
            response = requests.post(api_url, files=files, headers=headers, timeout=30)
            response.raise_for_status()
            
            extraction_data = response.json()
            
            # Store extraction results
            screenshot.extracted_text = extraction_data.get('text', '')
            screenshot.extraction_data = extraction_data
            screenshot.is_processed = True
            
            db.session.commit()
            
            return jsonify({
                'message': 'Screenshot data extracted successfully',
                'screenshot': screenshot.to_dict()
            }), 200
            
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Extraction API error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Extraction failed: {str(e)}'}), 500


@screenshot_bp.route('/session/<int:session_id>', methods=['GET'])
@jwt_required()
def get_session_screenshots(session_id):
    """Get all screenshots for a session"""
    employee_id = int(get_jwt_identity())
    employee = Employee.query.get(employee_id)
    
    session = MonitoringSession.query.get(session_id)
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    # Check access
    if employee.role != 'admin' and session.employee_id != employee_id:
        return jsonify({'error': 'Access denied'}), 403
    
    if employee.role == 'admin':
        session_employee = Employee.query.get(session.employee_id)
        if session_employee.organization_id != employee.organization_id:
            return jsonify({'error': 'Access denied'}), 403
    
    screenshots = Screenshot.query.filter_by(session_id=session_id).order_by(Screenshot.timestamp).all()
    
    return jsonify([s.to_dict() for s in screenshots]), 200
