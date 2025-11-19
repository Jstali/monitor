"""
Workflow Diagram Generator
Generates workflow diagrams from extracted screenshot data
"""

import json
from datetime import datetime
from collections import defaultdict

class WorkflowDiagramGenerator:
    def __init__(self, activities, screenshots):
        """
        Initialize with activities and screenshots data
        
        Args:
            activities: List of activity dictionaries
            screenshots: List of screenshot dictionaries with extraction data
        """
        self.activities = activities
        self.screenshots = screenshots
        
    def generate_mermaid_diagram(self):
        """Generate a detailed Mermaid flowchart with durations"""
        
        # Combine activities and screenshots
        events = []
        
        # Add activities
        for act in self.activities:
            events.append({
                'timestamp': act['timestamp'],
                'type': 'activity',
                'app': act.get('application_name') or act.get('url', 'Unknown'),
                'detail': act.get('window_title', '')
            })
            
        # Add processed screenshots
        for shot in self.screenshots:
            if shot.get('is_processed') and shot.get('extraction_data'):
                data = shot['extraction_data']
                if isinstance(data, dict) and 'app' in data:
                    events.append({
                        'timestamp': shot['timestamp'],
                        'type': 'screenshot',
                        'app': data['app'],
                        'action': data.get('action', ''),
                        'context': data.get('context', ''),
                        'detail': data.get('details', '')
                    })
        
        # Sort by timestamp
        events.sort(key=lambda x: x['timestamp'])
        
        # Generate Mermaid syntax
        mermaid = ["graph LR"]
        mermaid.append("    %% Styles")
        mermaid.append("    classDef appNode fill:#e1f5fe,stroke:#01579b,stroke-width:2px,rx:5,ry:5;")
        mermaid.append("    classDef webNode fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,rx:5,ry:5;")
        
        last_node_id = None
        last_timestamp = None
        
        for i, event in enumerate(events):
            node_id = f"N{i}"
            
            # Parse timestamp
            try:
                current_ts = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
            except:
                current_ts = datetime.now() # Fallback
            
            # Determine Label
            if event['type'] == 'screenshot':
                label = f"{event['app']}<br/>{event['action']}<br/><i>{event['context']}</i>"
            else:
                label = f"{event['app']}<br/>{event['detail'][:20]}..."
            
            label = label.replace('"', "'")
            mermaid.append(f"    {node_id}(\"{label}\")")
            
            # Styling
            if 'Chrome' in event['app'] or 'Safari' in event['app']:
                mermaid.append(f"    class {node_id} webNode;")
            else:
                mermaid.append(f"    class {node_id} appNode;")
            
            # Link to previous with duration
            if last_node_id and last_timestamp:
                duration = (current_ts - last_timestamp).total_seconds()
                minutes = int(duration / 60)
                seconds = int(duration % 60)
                
                duration_label = ""
                if minutes > 0:
                    duration_label = f"{minutes}m "
                duration_label += f"{seconds}s"
                
                mermaid.append(f"    {last_node_id} -- {duration_label} --> {node_id}")
            
            last_node_id = node_id
            last_timestamp = current_ts
            
        return "\n".join(mermaid)
    
    def generate_timeline_diagram(self):
        """Generate a timeline-based workflow diagram"""
        
        timeline = {
            'title': 'Employee Activity Timeline',
            'events': []
        }
        
        for activity in sorted(self.activities, key=lambda x: x['timestamp']):
            event = {
                'timestamp': activity['timestamp'],
                'type': activity['activity_type'],
                'description': activity.get('application_name') or activity.get('url', 'Unknown'),
                'details': activity.get('window_title', '')
            }
            timeline['events'].append(event)
        
        return timeline
    
    def generate_activity_summary(self):
        """Generate a summary of activities"""
        
        # Count by application
        app_counts = defaultdict(int)
        app_duration = defaultdict(int)
        
        for activity in self.activities:
            app_name = activity.get('application_name') or activity.get('url', 'Unknown')
            app_counts[app_name] += 1
            app_duration[app_name] += activity.get('duration_seconds', 0)
        
        # Sort by duration
        sorted_apps = sorted(app_duration.items(), key=lambda x: x[1], reverse=True)
        
        summary = {
            'total_activities': len(self.activities),
            'unique_applications': len(app_counts),
            'top_applications': [
                {
                    'name': app,
                    'duration_seconds': duration,
                    'count': app_counts[app]
                }
                for app, duration in sorted_apps[:10]
            ]
        }
        
        return summary
    
    def generate_screenshot_workflow(self):
        """Generate workflow from screenshot extraction data"""
        
        workflow_steps = []
        
        for screenshot in sorted(self.screenshots, key=lambda x: x['timestamp']):
            if screenshot.get('is_processed') and screenshot.get('extraction_data'):
                step = {
                    'timestamp': screenshot['timestamp'],
                    'extracted_text': screenshot.get('extracted_text', ''),
                    'data': screenshot.get('extraction_data', {})
                }
                workflow_steps.append(step)
        
        return {
            'total_screenshots': len(self.screenshots),
            'processed_screenshots': len([s for s in self.screenshots if s.get('is_processed')]),
            'workflow_steps': workflow_steps
        }
    
    def export_to_json(self, filepath):
        """Export all diagrams to JSON file"""
        
        data = {
            'generated_at': datetime.utcnow().isoformat(),
            'mermaid_diagram': self.generate_mermaid_diagram(),
            'timeline': self.generate_timeline_diagram(),
            'summary': self.generate_activity_summary(),
            'screenshot_workflow': self.generate_screenshot_workflow()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        return filepath
    
    def export_to_html(self, filepath):
        """Export workflow diagram as HTML with Mermaid rendering"""
        
        mermaid_diagram = self.generate_mermaid_diagram()
        timeline = self.generate_timeline_diagram()
        summary = self.generate_activity_summary()
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Workflow Diagram</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
            background: #f9fafb;
        }}
        .container {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        h1 {{ color: #1f2937; }}
        h2 {{ color: #374151; margin-top: 30px; }}
        .summary-item {{
            padding: 15px;
            background: #f3f4f6;
            border-radius: 8px;
            margin: 10px 0;
        }}
        .timeline-event {{
            padding: 12px;
            border-left: 3px solid #6366f1;
            margin: 10px 0;
            background: #f9fafb;
        }}
        .timestamp {{
            color: #6b7280;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Employee Activity Workflow</h1>
        <p class="timestamp">Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
        
        <h2>Activity Flow Diagram</h2>
        <div class="mermaid">
{mermaid_diagram}
        </div>
        
        <h2>Summary</h2>
        <div class="summary-item">
            <strong>Total Activities:</strong> {summary['total_activities']}<br>
            <strong>Unique Applications:</strong> {summary['unique_applications']}
        </div>
        
        <h3>Top Applications</h3>
        {''.join([f'''
        <div class="summary-item">
            <strong>{app['name']}</strong><br>
            Duration: {app['duration_seconds']}s | Count: {app['count']}
        </div>
        ''' for app in summary['top_applications']])}
        
        <h2>Timeline</h2>
        {''.join([f'''
        <div class="timeline-event">
            <div class="timestamp">{event['timestamp']}</div>
            <strong>{event['description']}</strong><br>
            <small>{event['details']}</small>
        </div>
        ''' for event in timeline['events'][:20]])}
    </div>
    
    <script>
        mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
    </script>
</body>
</html>
"""
        
        with open(filepath, 'w') as f:
            f.write(html)
        
        return filepath


# Example usage
if __name__ == '__main__':
    # Sample data
    activities = [
        {
            'timestamp': '2024-01-01T10:00:00',
            'activity_type': 'application',
            'application_name': 'VS Code',
            'window_title': 'main.py',
            'duration_seconds': 300
        },
        {
            'timestamp': '2024-01-01T10:05:00',
            'activity_type': 'website',
            'url': 'github.com',
            'window_title': 'GitHub - Repository',
            'duration_seconds': 120
        },
        {
            'timestamp': '2024-01-01T10:07:00',
            'activity_type': 'application',
            'application_name': 'Terminal',
            'window_title': 'bash',
            'duration_seconds': 180
        }
    ]
    
    screenshots = [
        {
            'timestamp': '2024-01-01T10:00:00',
            'is_processed': True,
            'extracted_text': 'Code editor with Python file',
            'extraction_data': {'text': 'def main()...'}
        }
    ]
    
    generator = WorkflowDiagramGenerator(activities, screenshots)
    
    # Generate diagrams
    print("Mermaid Diagram:")
    print(generator.generate_mermaid_diagram())
    print("\nTimeline:")
    print(json.dumps(generator.generate_timeline_diagram(), indent=2))
    print("\nSummary:")
    print(json.dumps(generator.generate_activity_summary(), indent=2))
    
    # Export to files
    generator.export_to_json('workflow.json')
    generator.export_to_html('workflow.html')
    print("\nExported to workflow.json and workflow.html")
