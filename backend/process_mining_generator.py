"""
Process Mining Workflow Generator
Generates process mining diagrams from screenshot activity data
Similar to Celonis/UiPath process maps with nodes, edges, and frequency counts
"""

import graphviz
from collections import defaultdict, Counter
from datetime import datetime
from models import Screenshot, Activity, MonitoringSession

class ProcessMiningGenerator:
    def __init__(self, session_id):
        """Initialize with a monitoring session ID"""
        self.session_id = session_id
        self.screenshots = []
        self.activities = []
        self.transitions = []
        self.activity_counts = Counter()
        self.transition_sequence = []  # Initialize transition sequence
        
    def load_data(self):
        """Load screenshots and activities from database"""
        session = MonitoringSession.query.get(self.session_id)
        if not session:
            raise ValueError(f"Session {self.session_id} not found")
        
        # Load screenshots with activity names
        self.screenshots = Screenshot.query.filter_by(
            session_id=self.session_id
        ).filter(
            Screenshot.activity_name.isnot(None)  # Only allowlisted screenshots
        ).order_by(Screenshot.timestamp).all()
        
        # Load activities
        self.activities = Activity.query.filter_by(
            session_id=self.session_id
        ).order_by(Activity.timestamp).all()
        
    def build_process_map(self):
        """Build process map from activity data"""
        # Extract activity sequence from screenshots
        activity_sequence = []
        
        for screenshot in self.screenshots:
            if screenshot.activity_name:
                activity_sequence.append(screenshot.activity_name)
        
        # Count activities
        self.activity_counts = Counter(activity_sequence)
        
        # Build transitions (edges) - KEEP FULL SEQUENCE for multiple arrows
        transition_counts = defaultdict(int)
        transition_sequence = []  # NEW: Store each transition individually
        
        for i in range(len(activity_sequence) - 1):
            from_activity = activity_sequence[i]
            to_activity = activity_sequence[i + 1]
            
            # Only count transitions between different activities
            if from_activity != to_activity:
                transition_counts[(from_activity, to_activity)] += 1
                # NEW: Store each transition with its sequence number
                transition_sequence.append({
                    'from': from_activity,
                    'to': to_activity,
                    'sequence': i + 1  # Sequence number for ordering
                })
        
        self.transitions = transition_counts
        self.transition_sequence = transition_sequence  # NEW: Full sequence
        
    def generate_graphviz_diagram(self, output_path='process_map.png'):
        """Generate professional process mining diagram using Graphviz"""
        dot = graphviz.Digraph(comment='Process Mining Map', engine='dot')
        
        # Graph attributes for horizontal flow
        dot.attr(rankdir='LR', splines='curved', nodesep='0.8', ranksep='1.5')
        dot.attr('graph', bgcolor='#f8f9fa', fontname='Arial', pad='0.5')
        dot.attr('node', fontname='Arial', fontsize='11')
        dot.attr('edge', fontname='Arial', fontsize='10')
        
        # Define professional color palette
        colors = {
            'start': '#4CAF50',      # Green for start
            'end': '#F44336',        # Red for end
            'high_freq': '#2196F3',  # Blue for high frequency
            'med_freq': '#64B5F6',   # Light blue for medium
            'low_freq': '#BBDEFB',   # Very light blue for low
            'edge': '#607D8B'        # Gray for edges
        }
        
        if not self.activity_counts:
            # No data - create empty diagram
            dot.node('no_data', 'No Activity Data', 
                    shape='box', style='filled,rounded', 
                    fillcolor='#E0E0E0', color='#9E9E9E')
            dot.render(output_path.replace('.png', ''), format='png', cleanup=True)
            return output_path
        
        # Add START node
        dot.node('START', 'START', 
                shape='circle', style='filled', 
                fillcolor=colors['start'], fontcolor='white', 
                width='0.8', height='0.8', fixedsize='true')
        
        # Add END node
        dot.node('END', 'END', 
                shape='circle', style='filled', 
                fillcolor=colors['end'], fontcolor='white',
                width='0.8', height='0.8', fixedsize='true')
        
        # Calculate frequency thresholds
        max_count = max(self.activity_counts.values()) if self.activity_counts else 1
        
        # Add activity nodes
        for activity, count in self.activity_counts.items():
            # Determine color based on frequency
            freq_ratio = count / max_count
            if freq_ratio >= 0.7:
                color = colors['high_freq']
            elif freq_ratio >= 0.3:
                color = colors['med_freq']
            else:
                color = colors['low_freq']
            
            # Create node label with activity name and count
            label = f"{activity}\\n({count})"
            
            # Create node with professional styling
            dot.node(activity, label,
                    shape='box', style='filled,rounded',
                    fillcolor=color, fontcolor='white',
                    color='#1976D2', penwidth='2',
                    margin='0.3,0.2')
        
        # Find first and last activities for START/END connections
        if self.screenshots:
            first_activity = self.screenshots[0].activity_name
            last_activity = self.screenshots[-1].activity_name
            
            # Connect START to first activity
            if first_activity:
                dot.edge('START', first_activity, 
                        label='1', color=colors['edge'], 
                        penwidth='1.5', fontcolor='#424242')
            
            # Connect last activity to END
            if last_activity:
                dot.edge(last_activity, 'END', 
                        label='1', color=colors['edge'], 
                        penwidth='1.5', fontcolor='#424242')
        
        # Add transition edges
        max_transition = max(self.transitions.values()) if self.transitions else 1
        
        for (from_act, to_act), count in self.transitions.items():
            # Edge thickness based on frequency
            freq_ratio = count / max_transition
            if freq_ratio >= 0.7:
                penwidth = '4.0'
                color = colors['high_freq']
            elif freq_ratio >= 0.3:
                penwidth = '2.5'
                color = colors['med_freq']
            else:
                penwidth = '1.5'
                color = colors['low_freq']
            
            # Edge label with count
            label = str(count)
            
            # Create edge
            dot.edge(from_act, to_act, 
                    label=label, 
                    penwidth=penwidth, 
                    color=color,
                    fontcolor='#424242',
                    labelfontsize='10')
        
        # Render diagram
        try:
            dot.render(output_path.replace('.png', ''), format='png', cleanup=True)
            return output_path
        except Exception as e:
            print(f"Error rendering diagram: {e}")
            return None
    
    def generate_pm4py_diagram(self, output_path='process_map_pm4py.png'):
        """Generate process mining diagram using PM4Py (alternative method)"""
        try:
            import pm4py
            import pandas as pd
            
            # Create event log DataFrame
            events = []
            case_id = f"session_{self.session_id}"
            
            for screenshot in self.screenshots:
                if screenshot.activity_name:
                    events.append({
                        'case:concept:name': case_id,
                        'concept:name': screenshot.activity_name,
                        'time:timestamp': screenshot.timestamp
                    })
            
            if not events:
                print("No events to process")
                return None
            
            df = pd.DataFrame(events)
            df['time:timestamp'] = pd.to_datetime(df['time:timestamp'])
            
            # Convert to event log
            event_log = pm4py.format_dataframe(df, case_id='case:concept:name', 
                                               activity_key='concept:name', 
                                               timestamp_key='time:timestamp')
            
            # Discover process model using Directly-Follows Graph
            dfg, start_activities, end_activities = pm4py.discover_dfg(event_log)
            
            # Visualize
            pm4py.view_dfg(dfg, start_activities, end_activities, 
                          format='png', file_path=output_path)
            
            return output_path
            
        except ImportError:
            print("PM4Py not installed. Using Graphviz instead.")
            return self.generate_graphviz_diagram(output_path)
    
    def export_event_log_csv(self, output_path='event_log.csv'):
        """Export event log as CSV for external process mining tools"""
        import csv
        
        with open(output_path, 'w', newline='') as csvfile:
            fieldnames = ['CaseID', 'Timestamp', 'Activity', 'Folder']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            case_id = f"session_{self.session_id}"
            
            for screenshot in self.screenshots:
                if screenshot.activity_name:
                    writer.writerow({
                        'CaseID': case_id,
                        'Timestamp': screenshot.timestamp.isoformat(),
                        'Activity': screenshot.activity_name,
                        'Folder': screenshot.folder_name
                    })
        
        return output_path
    
    def get_statistics(self):
        """Get process mining statistics"""
        total_activities = len(self.screenshots)
        unique_activities = len(self.activity_counts)
        total_transitions = sum(self.transitions.values())
        
        return {
            'total_activities': total_activities,
            'unique_activities': unique_activities,
            'total_transitions': total_transitions,
            'activity_distribution': dict(self.activity_counts),
            'top_transitions': sorted(self.transitions.items(), 
                                     key=lambda x: x[1], reverse=True)[:10],
            'transition_sequence': self.transition_sequence  # NEW: Full sequence for multiple arrows
        }


# Example usage
if __name__ == '__main__':
    # Generate process map for a session
    generator = ProcessMiningGenerator(session_id=1)
    generator.load_data()
    generator.build_process_map()
    
    # Generate diagram
    diagram_path = generator.generate_graphviz_diagram('workflow_diagram.png')
    print(f"Process map generated: {diagram_path}")
    
    # Export event log
    csv_path = generator.export_event_log_csv('event_log.csv')
    print(f"Event log exported: {csv_path}")
    
    # Print statistics
    stats = generator.get_statistics()
    print(f"Statistics: {stats}")
