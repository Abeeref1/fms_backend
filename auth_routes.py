# src/routes/auth_routes.py
from flask import Blueprint, request, jsonify, current_app
from src import db # Changed to absolute import
from src.models import Stakeholder # Changed to absolute import
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/api/v1/auth")

@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticates a stakeholder and returns JWT tokens."""
    email = None # Initialize email for logging in except block
    try:
        data = request.get_json()
        if not data:
            current_app.logger.warning("Login attempt with non-JSON body")
            return jsonify({"error": "Request body must be JSON"}), 400
            
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            current_app.logger.warning(f"Login attempt with missing credentials for email: {email}")
            return jsonify({"error": "Email and password are required"}), 400

        stakeholder = Stakeholder.query.filter_by(contact_email=email).first()

        # Use a separate check for stakeholder existence before checking password
        if not stakeholder:
            current_app.logger.warning(f"Login failed: User not found for email: {email}")
            return jsonify({"error": "Invalid credentials"}), 401
            
        if not stakeholder.check_password(password):
            current_app.logger.warning(f"Login failed: Invalid password for email: {email}")
            return jsonify({"error": "Invalid credentials"}), 401

        # Check if active *after* password check
        if not stakeholder.is_active:
             current_app.logger.warning(f"Login failed: User account inactive for email: {email}")
             return jsonify({"error": "User account is inactive"}), 401
             
        # Identity can be the stakeholder's ID or email
        identity = str(stakeholder.id) 
        
        # Add user claims (e.g., role) to the access token
        additional_claims = {"role": stakeholder.role, "name": stakeholder.name}
        
        access_token = create_access_token(identity=identity, additional_claims=additional_claims)
        refresh_token = create_refresh_token(identity=identity)
        
        current_app.logger.info(f"Login successful for user: {email}")
        return jsonify({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": stakeholder.to_dict() # Return basic user info (without sensitive data)
        }), 200
            
    except Exception as e:
        # Log the full error with stack trace for detailed debugging
        current_app.logger.error(f"Exception during login for {email if email else 'unknown user'}: {e}", exc_info=True)
        return jsonify({"error": "An internal server error occurred during login."}), 500

@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True) # Requires a valid refresh token
def refresh():
    """Provides a new access token using a refresh token."""
    identity = None # Initialize for logging
    try:
        identity = get_jwt_identity()
        # Fetch stakeholder to get updated claims if necessary
        stakeholder = Stakeholder.query.get(identity) 
        if not stakeholder or not stakeholder.is_active:
            current_app.logger.warning(f"Token refresh failed: User not found or inactive for identity: {identity}")
            return jsonify({"error": "User not found or inactive"}), 401
            
        additional_claims = {"role": stakeholder.role, "name": stakeholder.name}
        new_access_token = create_access_token(identity=identity, additional_claims=additional_claims)
        current_app.logger.info(f"Token refresh successful for identity: {identity}")
        return jsonify(access_token=new_access_token), 200
    except Exception as e:
        current_app.logger.error(f"Exception during token refresh for identity {identity if identity else 'unknown'}: {e}", exc_info=True)
        return jsonify({"error": "An internal server error occurred during token refresh."}), 500

# Optional: Add a registration route if needed
# @auth_bp.route("/register", methods=["POST"])
# def register():
#     # ... implementation ...

# Optional: Add a route to get current user info based on token
@auth_bp.route("/me", methods=["GET"])
@jwt_required() # Requires a valid access token
def get_current_user():
    """Returns information about the currently authenticated user."""
    identity = None # Initialize for logging
    try:
        identity = get_jwt_identity()
        stakeholder = Stakeholder.query.get(identity)
        if not stakeholder:
            current_app.logger.warning(f"Get current user failed: User not found for identity: {identity}")
            return jsonify({"error": "User not found"}), 404
        # No need to log success here as it might be frequent
        return jsonify(user=stakeholder.to_dict()), 200
    except Exception as e:
        current_app.logger.error(f"Exception fetching current user for identity {identity if identity else 'unknown'}: {e}", exc_info=True)
        return jsonify({"error": "An internal server error occurred fetching user details."}), 500

