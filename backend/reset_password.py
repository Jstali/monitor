from app import create_app
from models import db, Employee

app = create_app()
with app.app_context():
    employee = Employee.query.filter_by(email='stalinj4747@gmail.com').first()
    if employee:
        employee.set_password('password123')
        db.session.commit()
        print("Password reset successfully")
    else:
        print("Employee not found")
