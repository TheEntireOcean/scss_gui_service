# app/utils/__init__.py
from app import create_app, db
from app.models.user import User

def initialize_database():
    from app.services.auth_service import AuthService  # Lazy import inside function
    app = create_app()
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Create default admin user
        auth_service = AuthService()
        admin_user = auth_service.create_user(
            username='admin',
            password='admin123',
            role='admin'
        )
        
        if admin_user:
            print("Default admin user created: admin/admin123")
        else:
            print("Admin user already exists")

if __name__ == '__main__':
    initialize_database()