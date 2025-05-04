import click
from flask.cli import with_appcontext
from src import db # Assuming db is initialized in src/__init__.py or similar
from src.models import Stakeholder # Assuming Stakeholder model is in src/models.py or src/models/stakeholder.py

@click.command("create-admin")
@click.option("--email", required=True, help="Email address for the admin user.")
@click.option("--password", required=True, help="Password for the admin user.")
# Add other necessary fields like name, role etc. as options if needed
# @click.option("--name", required=True, help="Name for the admin user.")
@with_appcontext
def create_admin(email, password):
    """Creates or updates an admin user."""
    try:
        # Check if user already exists
        user = Stakeholder.query.filter_by(contact_email=email).first()
        
        if user:
            click.echo(f"User with email {email} already exists. Updating password and ensuring admin role.")
            # Ensure the user has the admin role (adjust role value as needed)
            user.role = "admin" 
        else:
            click.echo(f"Creating new admin user with email {email}.")
            # Create new user - ensure all required fields are provided
            # You might need to add more @click.option decorators for required fields
            user = Stakeholder(
                contact_email=email, 
                name="Admin User", # Example: Add a name option or use a default
                role="admin", # Set the role to admin
                is_active=True # Ensure the user is active
                # Add other required fields from your Stakeholder model here
            )
            db.session.add(user)

        # Set/update the password
        user.set_password(password)
        
        db.session.commit()
        click.echo(f"Successfully created/updated admin user: {email}")

    except Exception as e:
        db.session.rollback() # Rollback in case of error
        click.echo(f"Error creating/updating admin user {email}: {e}", err=True)

