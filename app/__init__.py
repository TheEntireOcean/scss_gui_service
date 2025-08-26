from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from graphene import Schema
from flask_graphql import GraphQLView
import os

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
socketio = SocketIO()

def create_app(config_class='app.config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    
    # Initialize SocketIO with CORS enabled
    socketio.init_app(app, 
                     cors_allowed_origins="*",
                     async_mode='eventlet',
                     logger=True,
                     engineio_logger=True)

    # Register blueprints or views
    from app.graphql.schema import Query, Mutation
    schema = Schema(query=Query, mutation=Mutation)

    app.add_url_rule(
        '/graphql',
        view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True)
    )

    # Register SocketIO event handlers
    from app.socketio_handlers import register_handlers
    register_handlers(socketio)

    # Import models to register them with SQLAlchemy
    from app.models import user, camera, person, system_config

    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()

    return app