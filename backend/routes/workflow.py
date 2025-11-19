from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Employee, MonitoringSession, Activity, Screenshot
from workflow_generator import WorkflowDiagramGenerator
import os
import tempfile

workflow_bp = Blueprint('workflow', __name__)

@workflow_bp.route('/session/<int:session_id>/diagram', methods=['GET'])
@jwt_required()
def generate_session_diagram(session_id):
    """Generate workflow diagram for a session"""
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
    
    # Get activities and screenshots
    activities = Activity.query.filter_by(session_id=session_id).all()
    screenshots = Screenshot.query.filter_by(session_id=session_id).all()
    
    # Convert to dictionaries
    activities_data = [a.to_dict() for a in activities]
    screenshots_data = [s.to_dict() for s in screenshots]
    
    # Generate diagrams
    generator = WorkflowDiagramGenerator(activities_data, screenshots_data)
    
    format_type = request.args.get('format', 'json')
    
    if format_type == 'html':
        # Generate HTML file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False)
        filepath = generator.export_to_html(temp_file.name)
        temp_file.close()
        
        return send_file(filepath, mimetype='text/html', as_attachment=True, 
                        download_name=f'workflow_session_{session_id}.html')
    
    elif format_type == 'json':
        # Generate JSON file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        filepath = generator.export_to_json(temp_file.name)
        temp_file.close()
        
        return send_file(filepath, mimetype='application/json', as_attachment=True,
                        download_name=f'workflow_session_{session_id}.json')
    
    else:
        # Return inline JSON
        return jsonify({
            'mermaid_diagram': generator.generate_mermaid_diagram(),
            'timeline': generator.generate_timeline_diagram(),
            'summary': generator.generate_activity_summary(),
            'screenshot_workflow': generator.generate_screenshot_workflow()
        }), 200


@workflow_bp.route('/employee/<int:emp_id>/diagram', methods=['GET'])
@jwt_required()
def generate_employee_diagram(emp_id):
    """Generate workflow diagram for all employee sessions"""
    current_employee_id = int(get_jwt_identity())
    current_employee = Employee.query.get(current_employee_id)
    
    # Check access
    if current_employee.role != 'admin' and current_employee.id != emp_id:
        return jsonify({'error': 'Access denied'}), 403
    
    employee = Employee.query.get(emp_id)
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404
    
    if current_employee.role == 'admin':
        if employee.organization_id != current_employee.organization_id:
            return jsonify({'error': 'Access denied'}), 403
    
    # Get all sessions for employee
    sessions = MonitoringSession.query.filter_by(employee_id=emp_id).all()
    session_ids = [s.id for s in sessions]
    
    # Get all activities and screenshots
    activities = Activity.query.filter(Activity.session_id.in_(session_ids)).all()
    screenshots = Screenshot.query.filter(Screenshot.session_id.in_(session_ids)).all()
    
    # Convert to dictionaries
    activities_data = [a.to_dict() for a in activities]
    screenshots_data = [s.to_dict() for s in screenshots]
    
    # Generate diagrams
    generator = WorkflowDiagramGenerator(activities_data, screenshots_data)
    
    format_type = request.args.get('format', 'json')
    
    if format_type == 'html':
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False)
        filepath = generator.export_to_html(temp_file.name)
        temp_file.close()
        
        return send_file(filepath, mimetype='text/html', as_attachment=True,
                        download_name=f'workflow_employee_{emp_id}.html')
    
    else:
        return jsonify({
            'mermaid_diagram': generator.generate_mermaid_diagram(),
            'timeline': generator.generate_timeline_diagram(),
            'summary': generator.generate_activity_summary(),
            'screenshot_workflow': generator.generate_screenshot_workflow()
        }), 200
