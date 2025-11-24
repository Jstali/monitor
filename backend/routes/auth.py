from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, Employee, Organization

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new employee"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    # Check if employee exists
    if Employee.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    # Get or create organization
    org_name = data.get('organization_name', 'Default Organization')
    organization = Organization.query.filter_by(name=org_name).first()
    if not organization:
        organization = Organization(name=org_name)
        db.session.add(organization)
        db.session.flush()
    
    # Get requested role (employee, admin, or super_admin)
    role = data.get('role', 'employee')
    
    # Validate role
    if role not in ['employee', 'admin', 'super_admin']:
        role = 'employee'
    
    # Create employee
    employee = Employee(
        email=data['email'],
        name=data['name'],
        organization_id=organization.id,
        role=role
    )
    employee.set_password(data['password'])
    
    # Note: Manager assignment is done manually by super admin
    # This allows flexibility for project-based reassignments
    
    db.session.add(employee)
    db.session.commit()
    
    return jsonify({
        'message': f'Registered successfully as {role}.',
        'employee': employee.to_dict()
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login employee"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    employee = Employee.query.filter_by(email=data['email']).first()
    
    if not employee or not employee.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not employee.is_active:
        return jsonify({'error': 'Account is inactive'}), 403
    
    # Create access token (identity must be string)
    access_token = create_access_token(identity=str(employee.id))
    
    return jsonify({
        'access_token': access_token,
        'employee': employee.to_dict()
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current logged in user"""
    employee_id = int(get_jwt_identity())
    employee = Employee.query.get(employee_id)
    
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404
    
    return jsonify(employee.to_dict()), 200
