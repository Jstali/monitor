from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Employee, MonitoringSession, Screenshot, Activity
from werkzeug.utils import secure_filename
import os
import requests
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

screenshot_bp = Blueprint('screenshots', __name__)

@screenshot_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_screenshot():
    """Upload a screenshot with dynamic folder routing"""
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
    
    # Get folder_name and activity_name from request (sent by agent based on allowlist)
    folder_name = request.form.get('folder_name')
    activity_name = request.form.get('activity_name', folder_name)
    
    # If no folder specified, skip (not in allowlist)
    if not folder_name:
        return jsonify({
            'message': 'Screenshot not saved - not in allowlist',
            'allowlist_filtered': True
        }), 200
    
    # Generate unique filename
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    filename = secure_filename(f"screenshot_{employee_id}_{active_session.id}_{timestamp}.png")
    
    # Create dynamic folder path
    folder_path = os.path.join(current_app.config['SCREENSHOT_FOLDER'], folder_name)
    os.makedirs(folder_path, exist_ok=True)
    
    filepath = os.path.join(folder_path, filename)
    file.save(filepath)
    
    file_size = os.path.getsize(filepath)
    
    # Create screenshot record with folder and activity info
    screenshot = Screenshot(
        session_id=active_session.id,
        file_path=filepath,
        file_size=file_size,
        folder_name=folder_name,
        activity_name=activity_name
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
    ocr_enabled = current_app.config.get('OCR_ENABLED', True)
    api_key = current_app.config.get('MISTRAL_API_KEY')
    api_url = current_app.config.get('MISTRAL_API_URL')
    
    # Use Mistral OCR if enabled and configured
    if ocr_enabled and api_key:
        try:
            from ocr_service import create_ocr_service
            
            logger.info(f"Using Mistral OCR for screenshot {screenshot_id}")
            
            # Create OCR service
            ocr_service = create_ocr_service(api_key, api_url)
            
            # Extract text and data
            extracted_text, extraction_data = ocr_service.extract_text_from_image(screenshot.file_path)
            
            # Store extraction results
            screenshot.extracted_text = extracted_text
            screenshot.extraction_data = extraction_data
            screenshot.is_processed = True
            
            db.session.commit()
            
            return jsonify({
                'message': 'Screenshot data extracted successfully using Mistral OCR',
                'screenshot': screenshot.to_dict()
            }), 200
            
        except Exception as e:
            logger.error(f"Mistral OCR failed: {str(e)}, falling back to activity data")
            # Fall through to fallback mechanism
    
    # FALLBACK: Use activity data if OCR is disabled or fails
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
            'source': 'activity_log_fallback'
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
            'source': 'fallback'
        }
        mock_text = "No activity data available for this screenshot"
    
    screenshot.extracted_text = mock_text
    screenshot.extraction_data = mock_data
    screenshot.is_processed = True
    
    db.session.commit()
    
    return jsonify({
        'message': 'Screenshot data extracted using fallback method',
        'screenshot': screenshot.to_dict()
    }), 200


@screenshot_bp.route('/extract/batch', methods=['POST'])
@jwt_required()
def extract_batch():
    """Batch extract data from multiple screenshots"""
    employee_id = int(get_jwt_identity())
    employee = Employee.query.get(employee_id)
    
    data = request.get_json()
    if not data or 'screenshot_ids' not in data:
        return jsonify({'error': 'No screenshot_ids provided'}), 400
        
    screenshot_ids = data['screenshot_ids']
    if not isinstance(screenshot_ids, list):
        return jsonify({'error': 'screenshot_ids must be a list'}), 400
        
    # Limit batch size
    if len(screenshot_ids) > 50:
        return jsonify({'error': 'Batch size limit exceeded (max 50)'}), 400
        
    # Get screenshots
    screenshots = Screenshot.query.filter(Screenshot.id.in_(screenshot_ids)).all()
    
    # Filter accessible screenshots
    valid_screenshots = []
    for s in screenshots:
        session = MonitoringSession.query.get(s.session_id)
        
        # Check access
        has_access = False
        if employee.role == 'admin':
            session_employee = Employee.query.get(session.employee_id)
            if session_employee.organization_id == employee.organization_id:
                has_access = True
        elif session.employee_id == employee_id:
            has_access = True
            
        if has_access and not s.is_processed and os.path.exists(s.file_path):
            valid_screenshots.append(s)
            
    if not valid_screenshots:
        return jsonify({'message': 'No valid unprocessed screenshots found'}), 200
        
    # Prepare for extraction
    ocr_enabled = current_app.config.get('OCR_ENABLED', True)
    api_key = current_app.config.get('MISTRAL_API_KEY')
    api_url = current_app.config.get('MISTRAL_API_URL')
    
    processed_count = 0
    failed_count = 0
    
    # Try OCR first if enabled
    if ocr_enabled and api_key:
        try:
            from ocr_service import create_ocr_service
            ocr_service = create_ocr_service(api_key, api_url)
            
            # Map paths to screenshot objects
            path_to_screenshot = {s.file_path: s for s in valid_screenshots}
            paths = list(path_to_screenshot.keys())
            
            # Run parallel extraction
            logger.info(f"Starting batch extraction for {len(paths)} screenshots")
            results = ocr_service.extract_batch_parallel(paths, max_workers=5)
            
            # Process results
            for path, (text, data) in results.items():
                screenshot = path_to_screenshot.get(path)
                if screenshot and text:
                    screenshot.extracted_text = text
                    screenshot.extraction_data = data
                    screenshot.is_processed = True
                    processed_count += 1
                else:
                    failed_count += 1
                    
            db.session.commit()
            
            # If some failed, fall back for those
            if failed_count > 0:
                logger.warning(f"OCR failed for {failed_count} screenshots, using fallback")
            else:
                return jsonify({
                    'message': f'Batch processing completed. Success: {processed_count}, Failed: {failed_count}',
                    'processed_count': processed_count,
                    'failed_count': failed_count
                }), 200
            
        except Exception as e:
            logger.error(f"Batch extraction failed: {str(e)}, falling back to activity data")
            # Fall through to fallback mechanism
    
    # FALLBACK: Use activity data for all unprocessed screenshots
    logger.info(f"Using fallback extraction for {len(valid_screenshots)} screenshots")
    
    for screenshot in valid_screenshots:
        if screenshot.is_processed:
            continue  # Skip already processed ones
            
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
                'source': 'activity_log_fallback'
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
                'source': 'fallback'
            }
            mock_text = "No activity data available for this screenshot"
        
        screenshot.extracted_text = mock_text
        screenshot.extraction_data = mock_data
        screenshot.is_processed = True
        processed_count += 1
    
    db.session.commit()
    
    return jsonify({
        'message': f'Batch processing completed using fallback. Success: {processed_count}',
        'processed_count': processed_count,
        'failed_count': 0
    }), 200


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
