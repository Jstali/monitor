from app import create_app
from models import db, Employee
import bcrypt

app = create_app()

with app.app_context():
    # Find Alice
    alice = Employee.query.filter_by(email='strawhatluff124@gmail.com').first()
    if alice:
        # Reset back to user's original password
        password = 'test@123'
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        alice.password_hash = hashed
        db.session.commit()
        print(f"✓ Reset password for {alice.name} back to 'test@123'")
    else:
        print("✗ Alice not found!")
