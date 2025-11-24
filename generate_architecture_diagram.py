"""
Generate architecture diagram for allowlist monitoring system
"""

import graphviz

def create_architecture_diagram():
    """Create system architecture diagram"""
    dot = graphviz.Digraph(comment='Allowlist Monitoring Architecture')
    dot.attr(rankdir='TB')
    dot.attr('node', shape='box', style='filled,rounded', fontname='Arial')
    
    # Define colors
    manager_color = '#FFE5B4'  # Peach
    agent_color = '#B4D7FF'    # Light blue
    backend_color = '#D4FFB4'  # Light green
    storage_color = '#FFB4D4'  # Light pink
    
    # Manager Layer
    with dot.subgraph(name='cluster_manager') as c:
        c.attr(label='Manager Dashboard', style='filled', color='lightgrey')
        c.node('manager_ui', 'Web UI\n(React)', fillcolor=manager_color)
        c.node('config_ui', 'Allowlist Config\n(Add/Edit/Delete)', fillcolor=manager_color)
    
    # Agent Layer
    with dot.subgraph(name='cluster_agent') as c:
        c.attr(label='Monitoring Agent (Employee Machine)', style='filled', color='lightgrey')
        c.node('agent_login', 'Login &\nFetch Allowlist', fillcolor=agent_color)
        c.node('agent_check', '10-Second Check\n(Allowlist Filter)', fillcolor=agent_color)
        c.node('agent_capture', 'Screenshot Capture\n(If Match)', fillcolor=agent_color)
    
    # Backend Layer
    with dot.subgraph(name='cluster_backend') as c:
        c.attr(label='Backend API (Flask)', style='filled', color='lightgrey')
        c.node('api_config', '/api/monitoring-config\n(CRUD)', fillcolor=backend_color)
        c.node('api_upload', '/api/screenshots/upload\n(Folder Routing)', fillcolor=backend_color)
        c.node('api_process', '/api/workflow/process-map\n(Process Mining)', fillcolor=backend_color)
    
    # Storage Layer
    with dot.subgraph(name='cluster_storage') as c:
        c.attr(label='Data Storage', style='filled', color='lightgrey')
        c.node('db_config', 'monitoring_configs\n(Allowlist)', fillcolor=storage_color)
        c.node('db_screenshots', 'screenshots\n(folder_name, activity_name)', fillcolor=storage_color)
        c.node('folders', 'File System\n(Cursor/, ChatGPT/, etc.)', fillcolor=storage_color)
    
    # Process Mining
    c.node('process_mining', 'Process Mining\nGenerator\n(Graphviz)', fillcolor='#FFFFB4')
    
    # Connections - Manager Flow
    dot.edge('manager_ui', 'config_ui', label='Configure')
    dot.edge('config_ui', 'api_config', label='POST/PUT/DELETE')
    dot.edge('api_config', 'db_config', label='Save')
    
    # Connections - Agent Flow
    dot.edge('agent_login', 'api_config', label='GET /active')
    dot.edge('api_config', 'agent_login', label='Allowlist JSON')
    dot.edge('agent_login', 'agent_check', label='Start Loop')
    dot.edge('agent_check', 'agent_capture', label='If Match')
    dot.edge('agent_capture', 'api_upload', label='POST + metadata')
    dot.edge('api_upload', 'db_screenshots', label='Save record')
    dot.edge('api_upload', 'folders', label='Save file')
    
    # Connections - Process Mining Flow
    dot.edge('manager_ui', 'api_process', label='Request diagram')
    dot.edge('api_process', 'db_screenshots', label='Load data')
    dot.edge('db_screenshots', 'process_mining', label='Activity sequence')
    dot.edge('process_mining', 'manager_ui', label='PNG/CSV/JSON')
    
    # Render
    dot.render('architecture_diagram', format='png', cleanup=True)
    print("✓ Architecture diagram generated: architecture_diagram.png")

if __name__ == '__main__':
    create_architecture_diagram()
