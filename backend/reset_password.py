from app import create_app
from models import db, Employee

app = create_app()
with app.app_context():
    employee = Employee.query.filter_by(email='stalinj4747@gmail.com').first()
    if employee:
        employee.set_password('test@123')
        db.session.commit()
        print(f"Password reset successfully for {employee.email}")
        print(f"New password: test@123")
    else:
        print("Employee not found")
