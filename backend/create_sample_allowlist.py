"""
Test script to create sample allowlist configurations
Run this after migration to set up initial allowlist for testing
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app import app
from models import db, MonitoringConfig, Organization

def create_sample_allowlist():
    """Create sample allowlist configurations"""
    with app.app_context():
        # Get first organization
        org = Organization.query.first()
        if not org:
            print("No organization found. Please create an organization first.")
            return
        
        print(f"Creating allowlist for organization: {org.name}")
        
        # Create sample configurations
        configs = [
            {
                'config_type': 'application',
                'pattern': 'Cursor',
                'folder_name': 'Cursor'
            },
            {
                'config_type': 'url',
                'pattern': 'chatgpt.com',
                'folder_name': 'ChatGPT'
            },
            {
                'config_type': 'application',
                'pattern': 'Slack',
                'folder_name': 'Slack'
            },
            {
                'config_type': 'url',
                'pattern': 'figma.com',
                'folder_name': 'Figma'
            }
        ]
        
        for config_data in configs:
            # Check if already exists
            existing = MonitoringConfig.query.filter_by(
                organization_id=org.id,
                pattern=config_data['pattern']
            ).first()
            
            if existing:
                print(f"  ⚠ Already exists: {config_data['pattern']}")
                continue
            
            config = MonitoringConfig(
                organization_id=org.id,
                **config_data
            )
            db.session.add(config)
            print(f"  ✓ Created: {config_data['config_type']} - {config_data['pattern']} → {config_data['folder_name']}/")
        
        db.session.commit()
        print("\n✓ Sample allowlist created successfully!")
        print("\nConfigured to monitor:")
        print("  - Cursor application → screenshots/Cursor/")
        print("  - ChatGPT website → screenshots/ChatGPT/")
        print("  - Slack application → screenshots/Slack/")
        print("  - Figma website → screenshots/Figma/")

if __name__ == '__main__':
    create_sample_allowlist()
