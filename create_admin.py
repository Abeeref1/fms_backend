#!/home/ubuntu/fms_backend/venv/bin/python
import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import create_app
from src import db
from src.models import Stakeholder

app = create_app()

with app.app_context():
    admin_email = "admin@example.com"
    admin_password = "FM-System-2025!"
    admin_name = "Admin User"
    admin_role = "Admin"

    # Check if user already exists
    existing_user = Stakeholder.query.filter_by(contact_email=admin_email).first()
    if existing_user:
        print(f"User with email \t{admin_email}\t already exists. Updating password...")
        try:
            existing_user.set_password(admin_password) # Update the password
            db.session.add(existing_user) # Stage the change
            db.session.commit() # Commit the change
            print(f"Password for admin user \t{admin_email}\t updated successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"Error updating password for admin user: {e}")
    else:
        print(f"Creating admin user: Email={admin_email}, Name={admin_name}, Role={admin_role}")
        try:
            new_admin = Stakeholder(
                name=admin_name,
                role=admin_role,
                contact_email=admin_email,
                contact_phone="N/A", # Add placeholder if required
                is_active=True
            )
            new_admin.set_password(admin_password) # Set the password
            db.session.add(new_admin)
            db.session.commit()
            print(f"Admin user \t{admin_email}\t created successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"Error creating admin user: {e}")

