from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Employee, MonitoringSession, Activity, encrypt_credentials, decrypt_credentials
from datetime import datetime

monitor_bp = Blueprint('monitoring', __name__)

@monitor_bp.route('/sessions/start', methods=['POST'])
@jwt_required()
def start_session():
    """Start a new monitoring session"""
    employee_id = int(get_jwt_identity())
    employee = Employee.query.get(employee_id)
    
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404
    
    # Check if there's an active session
    active_session = MonitoringSession.query.filter_by(
        employee_id=employee_id,
        is_active=True
    ).first()
    
    if active_session:
        return jsonify({'error': 'Active session already exists', 'session': active_session.to_dict()}), 400
    
    # Get credentials from request (optional - for agent authentication)
    data = request.get_json() or {}
    agent_email = data.get('agent_email')
    agent_password = data.get('agent_password')
    
    # If credentials provided, encrypt and store them
    if agent_email and agent_password:
        try:
            encrypted_creds = encrypt_credentials(agent_email, agent_password)
            employee.agent_credentials_encrypted = encrypted_creds
            db.session.commit()
        except Exception as e:
            return jsonify({'error': f'Failed to store credentials: {str(e)}'}), 500
    
    # Create new session
    session = MonitoringSession(employee_id=employee_id)
    db.session.add(session)
    db.session.commit()
    
    return jsonify({
        'message': 'Monitoring session started',
        'session': session.to_dict(),
        'screenshot_interval': employee.organization.screenshot_interval,
        'credentials_stored': bool(agent_email and agent_password)
    }), 201


@monitor_bp.route('/sessions/stop', methods=['POST'])
@jwt_required()
def stop_session():
    """Stop the active monitoring session"""
    employee_id = int(get_jwt_identity())
    
    active_session = MonitoringSession.query.filter_by(
        employee_id=employee_id,
        is_active=True
    ).first()
    
    if not active_session:
        return jsonify({'error': 'No active session found'}), 404
    
    active_session.end_time = datetime.utcnow()
    active_session.is_active = False
    db.session.commit()
    
    return jsonify({
        'message': 'Monitoring session stopped',
        'session': active_session.to_dict()
    }), 200


@monitor_bp.route('/sessions/current', methods=['GET'])
@jwt_required()
def get_current_session():
    """Get current active session"""
    employee_id = int(get_jwt_identity())
    
    active_session = MonitoringSession.query.filter_by(
        employee_id=employee_id,
        is_active=True
    ).first()
    
    if not active_session:
        return jsonify({'session': None}), 200
    
    return jsonify({'session': active_session.to_dict(include_details=True)}), 200


@monitor_bp.route('/sessions', methods=['GET'])
@jwt_required()
def get_sessions():
    """Get monitoring sessions (with filters)"""
    employee_id = int(get_jwt_identity())
    employee = Employee.query.get(employee_id)
    
    # Get query parameters
    target_employee_id = request.args.get('employee_id', type=int)
    limit = request.args.get('limit', 50, type=int)
    
    # Build query
    query = MonitoringSession.query
    
    if employee.role == 'admin':
        # Admin can view all sessions in their organization
        if target_employee_id:
            target_employee = Employee.query.get(target_employee_id)
            if not target_employee or target_employee.organization_id != employee.organization_id:
                return jsonify({'error': 'Access denied'}), 403
            query = query.filter_by(employee_id=target_employee_id)
        else:
            # Get all employees in organization
            org_employee_ids = [e.id for e in employee.organization.employees]
            query = query.filter(MonitoringSession.employee_id.in_(org_employee_ids))
    else:
        # Regular employees can only view their own sessions
        query = query.filter_by(employee_id=employee_id)
    
    sessions = query.order_by(MonitoringSession.start_time.desc()).limit(limit).all()
    
    return jsonify([s.to_dict() for s in sessions]), 200


@monitor_bp.route('/activities', methods=['POST'])
@jwt_required()
def log_activity():
    """Log an activity (application or website)"""
    employee_id = int(get_jwt_identity())
    
    # Get active session
    active_session = MonitoringSession.query.filter_by(
        employee_id=employee_id,
        is_active=True
    ).first()
    
    if not active_session:
        return jsonify({'error': 'No active session'}), 400
    
    data = request.get_json()
    
    if not data or not data.get('activity_type'):
        return jsonify({'error': 'Activity type required'}), 400
    
    activity = Activity(
        session_id=active_session.id,
        activity_type=data['activity_type'],
        application_name=data.get('application_name'),
        window_title=data.get('window_title'),
        url=data.get('url'),
        duration_seconds=data.get('duration_seconds', 0),
        in_allowlist=data.get('in_allowlist', False)  # NEW: Track if in allowlist
    )
    
    db.session.add(activity)
    db.session.commit()
    
    return jsonify(activity.to_dict()), 201


@monitor_bp.route('/activities', methods=['GET'])
@jwt_required()
def get_activities():
    """Get activities for a session"""
    employee_id = int(get_jwt_identity())
    employee = Employee.query.get(employee_id)
    
    session_id = request.args.get('session_id', type=int)
    
    if not session_id:
        return jsonify({'error': 'Session ID required'}), 400
    
    session = MonitoringSession.query.get(session_id)
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    # Check access
    if employee.role != 'admin' and session.employee_id != employee_id:
        return jsonify({'error': 'Access denied'}), 403
    
    if employee.role == 'admin':
        # Verify session belongs to organization
        session_employee = Employee.query.get(session.employee_id)
        if session_employee.organization_id != employee.organization_id:
            return jsonify({'error': 'Access denied'}), 403
    
    activities = Activity.query.filter_by(session_id=session_id).order_by(Activity.timestamp).all()
    
    return jsonify([a.to_dict() for a in activities]), 200


@monitor_bp.route('/agent/credentials', methods=['GET'])
@jwt_required()
def get_agent_credentials():
    """Get encrypted agent credentials for the authenticated employee"""
    employee_id = int(get_jwt_identity())
    employee = Employee.query.get(employee_id)
    
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404
    
    if not employee.agent_credentials_encrypted:
        return jsonify({'error': 'No agent credentials stored. Please provide credentials when starting a monitoring session.'}), 404
    
    try:
        email, password = decrypt_credentials(employee.agent_credentials_encrypted)
        return jsonify({
            'email': email,
            'password': password
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to decrypt credentials: {str(e)}'}), 500


@monitor_bp.route('/agent/credentials', methods=['PUT'])
@jwt_required()
def update_agent_credentials():
    """Update agent credentials for the authenticated employee"""
    employee_id = int(get_jwt_identity())
    employee = Employee.query.get(employee_id)
    
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404
    
    data = request.get_json()
    agent_email = data.get('agent_email')
    agent_password = data.get('agent_password')
    
    if not agent_email or not agent_password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    try:
        encrypted_creds = encrypt_credentials(agent_email, agent_password)
        employee.agent_credentials_encrypted = encrypted_creds
        db.session.commit()
        
        return jsonify({
            'message': 'Agent credentials updated successfully'
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to update credentials: {str(e)}'}), 500


@monitor_bp.route('/agent/credentials/status', methods=['GET'])
@jwt_required()
def get_credentials_status():
    """Check if agent credentials are stored"""
    employee_id = int(get_jwt_identity())
    employee = Employee.query.get(employee_id)
    
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404
    
    has_credentials = bool(employee.agent_credentials_encrypted)
    
    # If credentials exist, return masked email
    masked_email = None
    if has_credentials:
        try:
            email, _ = decrypt_credentials(employee.agent_credentials_encrypted)
            # Mask email: user@example.com -> u***@example.com
            if '@' in email:
                local, domain = email.split('@', 1)
                masked_email = f"{local[0]}***@{domain}" if len(local) > 1 else f"***@{domain}"
            else:
                masked_email = "***"
        except:
            masked_email = "***"
    
    return jsonify({
        'has_credentials': has_credentials,
        'masked_email': masked_email
    }), 200
