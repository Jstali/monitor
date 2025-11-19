from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Organization, Employee

org_bp = Blueprint('organizations', __name__)

@org_bp.route('/', methods=['GET'])
@jwt_required()
def get_organizations():
    """Get all organizations (admin only)"""
    employee_id = int(get_jwt_identity())
    employee = Employee.query.get(employee_id)
    
    if employee.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    organizations = Organization.query.all()
    return jsonify([org.to_dict() for org in organizations]), 200


@org_bp.route('/<int:org_id>', methods=['GET'])
@jwt_required()
def get_organization(org_id):
    """Get organization details"""
    employee_id = int(get_jwt_identity())
    employee = Employee.query.get(employee_id)
    
    # Employees can only view their own organization
    if employee.role != 'admin' and employee.organization_id != org_id:
        return jsonify({'error': 'Access denied'}), 403
    
    organization = Organization.query.get(org_id)
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    return jsonify(organization.to_dict()), 200


@org_bp.route('/<int:org_id>', methods=['PUT'])
@jwt_required()
def update_organization(org_id):
    """Update organization settings"""
    employee_id = int(get_jwt_identity())
    employee = Employee.query.get(employee_id)
    
    if employee.role != 'admin' or employee.organization_id != org_id:
        return jsonify({'error': 'Admin access required'}), 403
    
    organization = Organization.query.get(org_id)
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    data = request.get_json()
    
    if 'name' in data:
        organization.name = data['name']
    
    if 'screenshot_interval' in data:
        interval = data['screenshot_interval']
        if interval < 5 or interval > 300:
            return jsonify({'error': 'Screenshot interval must be between 5 and 300 seconds'}), 400
        organization.screenshot_interval = interval
    
    db.session.commit()
    
    return jsonify(organization.to_dict()), 200


@org_bp.route('/<int:org_id>/employees', methods=['GET'])
@jwt_required()
def get_organization_employees(org_id):
    """Get all employees in an organization"""
    employee_id = int(get_jwt_identity())
    employee = Employee.query.get(employee_id)
    
    if employee.role != 'admin' or employee.organization_id != org_id:
        return jsonify({'error': 'Admin access required'}), 403
    
    organization = Organization.query.get(org_id)
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    employees = Employee.query.filter_by(organization_id=org_id).all()
    return jsonify([emp.to_dict() for emp in employees]), 200
