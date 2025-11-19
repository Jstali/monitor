from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Employee

emp_bp = Blueprint('employees', __name__)

@emp_bp.route('/me', methods=['GET'])
@jwt_required()
def get_my_profile():
    """Get current employee profile"""
    employee_id = int(get_jwt_identity())
    employee = Employee.query.get(employee_id)
    
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404
    
    return jsonify(employee.to_dict(include_sessions=True)), 200


@emp_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_my_profile():
    """Update current employee profile"""
    employee_id = int(get_jwt_identity())
    employee = Employee.query.get(employee_id)
    
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404
    
    data = request.get_json()
    
    if 'name' in data:
        employee.name = data['name']
    
    if 'password' in data and data['password']:
        employee.set_password(data['password'])
    
    db.session.commit()
    
    return jsonify(employee.to_dict()), 200


@emp_bp.route('/<int:emp_id>', methods=['GET'])
@jwt_required()
def get_employee(emp_id):
    """Get employee details (admin only)"""
    current_employee_id = int(get_jwt_identity())
    current_employee = Employee.query.get(current_employee_id)
    
    if current_employee.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    employee = Employee.query.get(emp_id)
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404
    
    # Admin can only view employees in their organization
    if employee.organization_id != current_employee.organization_id:
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify(employee.to_dict(include_sessions=True)), 200


@emp_bp.route('/<int:emp_id>', methods=['PUT'])
@jwt_required()
def update_employee(emp_id):
    """Update employee (admin only)"""
    current_employee_id = int(get_jwt_identity())
    current_employee = Employee.query.get(current_employee_id)
    
    if current_employee.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    employee = Employee.query.get(emp_id)
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404
    
    if employee.organization_id != current_employee.organization_id:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    if 'name' in data:
        employee.name = data['name']
    
    if 'role' in data and data['role'] in ['admin', 'employee']:
        employee.role = data['role']
    
    if 'is_active' in data:
        employee.is_active = data['is_active']
    
    db.session.commit()
    
    return jsonify(employee.to_dict()), 200
