from flask import Flask
from flask_cors import CORS
from src.routes.auth_routes import auth_bp

def create_app():
    app = Flask(__name__)
    CORS(app, origins=["*"], supports_credentials=True)
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")

    @app.route("/")
    def hello():
        return "Hello from Smart FMS Backend!"

    return app

app = create_app()
