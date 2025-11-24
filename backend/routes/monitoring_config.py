from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Employee, MonitoringConfig
import logging

logger = logging.getLogger(__name__)

config_bp = Blueprint('monitoring_config', __name__)

@config_bp.route('/', methods=['GET'])
@jwt_required()
def get_configs():
    """Get all monitoring configurations for the organization"""
    employee_id = int(get_jwt_identity())
    employee = Employee.query.get(employee_id)
    
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404
    
    configs = MonitoringConfig.query.filter_by(
        organization_id=employee.organization_id
    ).order_by(MonitoringConfig.created_at.desc()).all()
    
    return jsonify([config.to_dict() for config in configs]), 200


@config_bp.route('/active', methods=['GET'])
@jwt_required()
def get_active_configs():
    """Get active monitoring configurations (for agent)"""
    employee_id = int(get_jwt_identity())
    employee = Employee.query.get(employee_id)
    
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404
    
    configs = MonitoringConfig.query.filter_by(
        organization_id=employee.organization_id,
        is_active=True
    ).all()
    
    return jsonify([config.to_dict() for config in configs]), 200


@config_bp.route('/', methods=['POST'])
@jwt_required()
def create_config():
    """Create a new monitoring configuration (admin only)"""
    employee_id = int(get_jwt_identity())
    employee = Employee.query.get(employee_id)
    
    if not employee or employee.role not in ['admin', 'super_admin']:
        return jsonify({'error': 'Access denied. Admin privileges required.'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    if not data or 'config_type' not in data or 'pattern' not in data or 'folder_name' not in data:
        return jsonify({'error': 'Missing required fields: config_type, pattern, folder_name'}), 400
    
    # Validate config_type
    if data['config_type'] not in ['application', 'url']:
        return jsonify({'error': 'Invalid config_type. Must be "application" or "url"'}), 400
    
    # Create new config
    config = MonitoringConfig(
        organization_id=employee.organization_id,
        config_type=data['config_type'],
        pattern=data['pattern'].strip(),
        folder_name=data['folder_name'].strip().replace(' ', '_'),
        is_active=data.get('is_active', True)
    )
    
    db.session.add(config)
    db.session.commit()
    
    logger.info(f"Monitoring config created: {config.id} by employee {employee_id}")
    
    return jsonify({
        'message': 'Monitoring configuration created successfully',
        'config': config.to_dict()
    }), 201


@config_bp.route('/<int:config_id>', methods=['PUT'])
@jwt_required()
def update_config(config_id):
    """Update a monitoring configuration (admin only)"""
    employee_id = int(get_jwt_identity())
    employee = Employee.query.get(employee_id)
    
    if not employee or employee.role not in ['admin', 'super_admin']:
        return jsonify({'error': 'Access denied. Admin privileges required.'}), 403
    
    config = MonitoringConfig.query.get(config_id)
    if not config:
        return jsonify({'error': 'Configuration not found'}), 404
    
    if config.organization_id != employee.organization_id:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    # Update fields
    if 'config_type' in data:
        if data['config_type'] not in ['application', 'url']:
            return jsonify({'error': 'Invalid config_type'}), 400
        config.config_type = data['config_type']
    
    if 'pattern' in data:
        config.pattern = data['pattern'].strip()
    
    if 'folder_name' in data:
        config.folder_name = data['folder_name'].strip().replace(' ', '_')
    
    if 'is_active' in data:
        config.is_active = data['is_active']
    
    db.session.commit()
    
    logger.info(f"Monitoring config updated: {config_id} by employee {employee_id}")
    
    return jsonify({
        'message': 'Monitoring configuration updated successfully',
        'config': config.to_dict()
    }), 200


@config_bp.route('/<int:config_id>', methods=['DELETE'])
@jwt_required()
def delete_config(config_id):
    """Delete a monitoring configuration (admin only)"""
    employee_id = int(get_jwt_identity())
    employee = Employee.query.get(employee_id)
    
    if not employee or employee.role not in ['admin', 'super_admin']:
        return jsonify({'error': 'Access denied. Admin privileges required.'}), 403
    
    config = MonitoringConfig.query.get(config_id)
    if not config:
        return jsonify({'error': 'Configuration not found'}), 404
    
    if config.organization_id != employee.organization_id:
        return jsonify({'error': 'Access denied'}), 403
    
    db.session.delete(config)
    db.session.commit()
    
    logger.info(f"Monitoring config deleted: {config_id} by employee {employee_id}")
    
    return jsonify({'message': 'Monitoring configuration deleted successfully'}), 200
