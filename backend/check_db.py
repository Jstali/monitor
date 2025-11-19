from app import create_app
from app import create_app
from models import Screenshot, MonitoringSession, Employee, Activity

app = create_app()
with app.app_context():
    employees = Employee.query.all()
    for e in employees:
        print(f"Employee: {e.name} ({e.email}), Role: {e.role}, Org ID: {e.organization_id}")
    
    sessions = MonitoringSession.query.all()
    print(f"Total sessions: {len(sessions)}")
    for s in sessions:
        s_count = Screenshot.query.filter_by(session_id=s.id).count()
        a_count = Activity.query.filter_by(session_id=s.id).count()
        print(f"Session {s.id} (Emp {s.employee_id}): {s_count} screenshots, {a_count} activities")
