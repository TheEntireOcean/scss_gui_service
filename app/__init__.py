from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_marshmallow import Marshmallow
import os

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
socketio = SocketIO()
ma = Marshmallow()

def create_app(config_class='app.config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    ma.init_app(app)
    
    # Initialize SocketIO with CORS enabled
    socketio.init_app(app, 
                     cors_allowed_origins="*",
                     async_mode='eventlet',
                     logger=True,
                     engineio_logger=True)

    # Register API blueprints
    from app.api.auth import auth_bp
    from app.api.cameras import cameras_bp
    from app.api.persons import persons_bp
    from app.api.system import system_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(cameras_bp)
    app.register_blueprint(persons_bp)
    app.register_blueprint(system_bp)

    # Register error handlers
    from app.api.middleware.error_handlers import register_error_handlers
    register_error_handlers(app)

    # Register SocketIO event handlers
    from app.socketio_handlers import register_handlers
    register_handlers(socketio)

    # Import models to register them with SQLAlchemy
    from app.models import user, camera, person, system_config

    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()

    return app