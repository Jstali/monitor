from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Employee, MonitoringSession, Activity, Screenshot
from workflow_generator import WorkflowDiagramGenerator
from process_mining_generator import ProcessMiningGenerator
import os
import tempfile

workflow_bp = Blueprint('workflow', __name__)

@workflow_bp.route('/session/<int:session_id>/process-map', methods=['GET'])
@jwt_required(optional=True)
def generate_process_map(session_id):
    """Generate process mining diagram for a session (allowlist-filtered)"""
    # Try to get employee_id from JWT (header or query param)
    try:
        employee_id = get_jwt_identity()
        if not employee_id:
            # Try query parameter token
            from flask_jwt_extended import decode_token
            token = request.args.get('token')
            if token:
                decoded = decode_token(token)
                employee_id = decoded['sub']
            else:
                return jsonify({'error': 'Authentication required'}), 401
        employee_id = int(employee_id)
    except Exception as e:
        return jsonify({'error': 'Invalid authentication'}), 401
    
    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404
    
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
    
    try:
        # Generate process mining diagram
        generator = ProcessMiningGenerator(session_id)
        generator.load_data()
        generator.build_process_map()
        
        format_type = request.args.get('format', 'json')
        
        if format_type == 'png':
            # Generate PNG diagram
            temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            diagram_path = generator.generate_graphviz_diagram(temp_file.name)
            
            return send_file(diagram_path, mimetype='image/png', as_attachment=False,
                           download_name=f'process_map_session_{session_id}.png')
        
        elif format_type == 'csv':
            # Export event log CSV
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
            csv_path = generator.export_event_log_csv(temp_file.name)
            
            return send_file(csv_path, mimetype='text/csv', as_attachment=True,
                           download_name=f'event_log_session_{session_id}.csv')
        
        else:  # json
            # Return statistics and data
            stats = generator.get_statistics()
            return jsonify({
                'statistics': stats,
                'activity_counts': dict(generator.activity_counts),
                'transitions': {f"{k[0]} → {k[1]}": v for k, v in generator.transitions.items()}
            }), 200
            
    except Exception as e:
        return jsonify({'error': f'Failed to generate process map: {str(e)}'}), 500


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
        
        # Return as inline content for modal display, not as download
        return send_file(filepath, mimetype='text/html', as_attachment=False)
    
    elif format_type == 'json':
        # Return JSON data directly for frontend consumption
        screenshot_workflow_data = generator.generate_screenshot_workflow()
        
        # Debug logging
        print(f"DEBUG: Total screenshots: {screenshot_workflow_data.get('total_screenshots')}")
        print(f"DEBUG: Processed screenshots: {screenshot_workflow_data.get('processed_screenshots')}")
        print(f"DEBUG: Workflow steps count: {len(screenshot_workflow_data.get('workflow_steps', []))}")
        
        # Create summary text from workflow items
        summary_text = []
        for item in screenshot_workflow_data.get('workflow_steps', []):
            text = f"{item['step']}. {item['app']}"
            if item.get('action'):
                text += f" → {item['action']}"
            if item.get('context'):
                text += f" ({item['context']}"
                if item.get('time_spent'):
                    text += f" - Time spent: {item['time_spent']}"
                text += ")"
            elif item.get('time_spent'):
                text += f" (Time spent: {item['time_spent']})"
            summary_text.append(text)
        
        print(f"DEBUG: Summary text lines: {len(summary_text)}")
        if summary_text:
            print(f"DEBUG: First line: {summary_text[0][:100]}")
        
        workflow_summary = '\n'.join(summary_text) if summary_text else 'No workflow data available'
        
        result = {
            'mermaid_diagram': generator.generate_mermaid_diagram(),
            'screenshot_workflow': workflow_summary,
            'activity_summary': generator.generate_activity_summary(),
            'timeline': generator.generate_timeline_diagram()
        }
        
        print(f"DEBUG: screenshot_workflow length: {len(result['screenshot_workflow'])}")
        
        return jsonify(result), 200
    
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
