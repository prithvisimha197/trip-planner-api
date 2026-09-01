from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
from config import config

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Setup logging FIRST
    from app.logging_config import setup_logging, log_request
    access_logger = setup_logging(app)
    log_request(app, access_logger)

    app.logger.info('Application starting', extra={
        'extra_data': {
            'config': config_name,
            'debug': app.config.get('DEBUG', False)
        }
    })

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)

    app.logger.info('Extensions initialized')

    # Register blueprints
    from app.routes import auth, trips, places
    app.register_blueprint(auth.bp)
    app.register_blueprint(trips.bp)
    app.register_blueprint(places.bp)

    app.logger.info('Blueprints registered', extra={
        'extra_data': {
            'blueprints': ['auth', 'trips', 'places']
        }
    })

    return app
