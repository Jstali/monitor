from app import create_app
from models import db, Employee

app = create_app()
app.config['TESTING'] = True

with app.app_context():
    print("Attempting to log in as Alice...")
    try:
        # Test direct database access first
        user = Employee.query.filter_by(email='strawhatluff124@gmail.com').first()
        if not user:
            print("Error: User not found in database!")
        else:
            print(f"User found: {user.name} (ID: {user.id})")
            print(f"Role: {user.role}")
            
            # Test login endpoint via test client
            client = app.test_client()
            res = client.post('/api/auth/login', json={
                'email': 'strawhatluff124@gmail.com',
                'password': 'password123'
            })
            print(f"Response Status: {res.status_code}")
            if res.status_code == 500:
                print("Response Data:", res.get_data(as_text=True))
            else:
                print("Login successful!")
                
    except Exception as e:
        print(f"EXCEPTION CAUGHT: {e}")
        import traceback
        traceback.print_exc()
