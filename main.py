import os
from flask import Flask, jsonify
from flask_migrate import Migrate, upgrade, init, migrate as flask_migrate_command
from flask_cors import CORS
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager # Import JWTManager

# Import db instance using absolute path from src
from src import db

# Load environment variables
load_dotenv()

# Initialize extensions (Migrate, JWT)
migrate_ext = Migrate()
jwt = JWTManager() # Initialize JWTManager

def create_app(config_name="development"):
    # Removed static_folder and static_url_path as this is API only
    app = Flask(__name__)

    # Configuration
    db_url = os.environ.get("DATABASE_URL", "sqlite:////home/ubuntu/fms_backend/fms_dev.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    # IMPORTANT: Use a strong, unique secret key from environment variables for production
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "a_very_secret_key_for_dev_only") 
    # Configure JWT - use the same secret key
    app.config["JWT_SECRET_KEY"] = app.config["SECRET_KEY"] 
    # Optional: Configure token expiration times (e.g., access tokens expire after 1 hour)
    # from datetime import timedelta
    # app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

    # Initialize extensions with app
    db.init_app(app)
    migrate_ext.init_app(app, db)
    # Updated CORS origin to match support request
    CORS(app, origins=["https://sgptiylq.manus.space"], supports_credentials=True)
    jwt.init_app(app) # Initialize JWT with app

    # Import models using absolute path from src
    from src.models import Region, School, Stakeholder, Asset, Manpower, Service, WorkOrder, WorkOrderCost, SLA, SLAResult, KPI, KPIResult, Invoice, Notification

    # Register Blueprints using absolute path from src
    try:
        from src.routes.region_routes import region_bp
        from src.routes.school_routes import school_bp
        from src.routes.stakeholder_routes import stakeholder_bp
        from src.routes.asset_routes import asset_bp
        from src.routes.manpower_routes import manpower_bp
        from src.routes.service_routes import service_bp
        from src.routes.work_order_routes import work_order_bp
        from src.routes.work_order_cost_routes import work_order_cost_bp
        from src.routes.sla_routes import sla_bp
        from src.routes.sla_result_routes import sla_result_bp
        from src.routes.kpi_routes import kpi_bp
        from src.routes.kpi_result_routes import kpi_result_bp
        from src.routes.invoice_routes import invoice_bp
        from src.routes.report_routes import report_bp
        from src.routes.notification_routes import notification_bp
        from src.routes.integration_routes import integration_bp
        from src.routes.auth_routes import auth_bp # Import the auth blueprint

        app.register_blueprint(region_bp)
        app.register_blueprint(school_bp)
        app.register_blueprint(stakeholder_bp)
        app.register_blueprint(asset_bp)
        app.register_blueprint(manpower_bp)
        app.register_blueprint(service_bp)
        app.register_blueprint(work_order_bp)
        app.register_blueprint(work_order_cost_bp)
        app.register_blueprint(sla_bp)
        app.register_blueprint(sla_result_bp)
        app.register_blueprint(kpi_bp)
        app.register_blueprint(kpi_result_bp)
        app.register_blueprint(invoice_bp)
        app.register_blueprint(report_bp)
        app.register_blueprint(notification_bp)
        app.register_blueprint(integration_bp)
        # Ensure auth_bp is registered with the correct prefix
        app.register_blueprint(auth_bp) # Already registered, prefix is defined in auth_routes.py
        print("Blueprints registered successfully.")
    except ImportError as e:
        print(f"ERROR: Failed to import or register blueprints: {e}")

    # Removed conflicting root route (".") - Use "/health" instead

    # Print the URL map for debugging
    print("--- Registered URL Map ---")
    print(app.url_map)
    print("------------------------")

    # Handle migrations programmatically within app context
    with app.app_context():
        migrations_dir = os.path.join(os.path.dirname(app.root_path), "migrations")
        print(f"Checking migrations directory: {migrations_dir}")
        try:
            if not os.path.exists(migrations_dir):
                print("Migrations directory not found. Initializing...")
                init(directory=migrations_dir)
                print("Migrations directory initialized.")
                print("Generating initial migration...")
                flask_migrate_command(directory=migrations_dir, message="Initial migration")
                print("Initial migration generated.")
            
            # Check if migration is needed for Stakeholder changes
            print("Generating potential migration for authentication fields...")
            try:
                # Generate migration script without applying it yet
                flask_migrate_command(directory=migrations_dir, message="Add auth fields to Stakeholder")
                print("Migration script generated (if changes detected). Applying migrations...")
            except Exception as migrate_gen_err:
                # This might fail if no changes are detected, which is okay
                print(f"Note: Migration generation might have failed if no changes detected: {migrate_gen_err}")
            
            # Apply any pending migrations
            upgrade(directory=migrations_dir)
            print("Database migrations applied successfully.")

        except Exception as e:
            print(f"Error during database migration setup: {e}")
            # Add more specific error handling if needed

    # Removed conflicting catch-all route (".") for serving frontend

    # Simple health check route
    @app.route("/health")
    def health_check():
        return jsonify({"message": "FMS Backend is running!"})

    return app

if __name__ == "__main__":
    # Ensure the parent directory (fms_backend) is in the Python path
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    
    app = create_app()
    # Ensure Gunicorn uses this app instance when run externally
    # The run command below is mainly for direct execution (python src/main.py)
    app.run(host="0.0.0.0", port=5003, debug=False)

