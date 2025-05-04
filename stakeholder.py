from .. import db # Import db from parent package (src)
from werkzeug.security import generate_password_hash, check_password_hash

class Stakeholder(db.Model):
    __tablename__ = 'stakeholders'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # e.g., Admin, FM Manager, Technician
    contact_email = db.Column(db.String(120), unique=True, nullable=False, index=True) # Added index for faster lookup
    contact_phone = db.Column(db.String(20), nullable=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=True) # Optional link to a specific school
    password_hash = db.Column(db.String(256), nullable=True) # Store hashed password, nullable for now
    is_active = db.Column(db.Boolean, default=True) # Flag for active users

    def set_password(self, password):
        """Hashes the password and stores it."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks if the provided password matches the stored hash."""
        if not self.password_hash:
            return False # No password set
        return check_password_hash(self.password_hash, password)

    def to_dict(self, include_sensitive=False):
        """Returns dictionary representation, optionally excluding sensitive info."""
        data = {
            'id': self.id,
            'name': self.name,
            'role': self.role,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone,
            'school_id': self.school_id,
            'is_active': self.is_active
        }
        # Never return password_hash directly
        return data

    # Properties and methods required by Flask-Login or similar (if used later)
    # For JWT, we primarily need an identifier (id or email)
    @property
    def is_authenticated(self):
        # In a real Flask-Login setup, this would check session status
        # For JWT, authentication is checked per request via token
        return True # Placeholder, actual check happens via @jwt_required

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        # Required by Flask-Login, returns a unicode identifier for the user
        return str(self.id)

