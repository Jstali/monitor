from app import create_app
from models import db, Employee
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Find Alice
    alice = Employee.query.filter_by(email='strawhatluff124@gmail.com').first()
    if alice:
        alice.password_hash = generate_password_hash('password123')
        db.session.commit()
        print(f"✓ Reset password for {alice.name} ({alice.email}) to 'password123'")
    else:
        print("✗ Alice not found!")
