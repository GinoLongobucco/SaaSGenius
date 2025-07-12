from flask import Flask
from flask_login import LoginManager
from config.settings import config
from app.database import db
from app.utils.monitoring import start_monitoring
from app.utils.async_analyzer import AsyncAnalysisManager
import logging
import os

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Si python-dotenv no está instalado, intentar cargar manualmente
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

# Initialize extensions
login_manager = LoginManager()
async_analyzer = AsyncAnalysisManager()

def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Handle both string config names and config objects
    if isinstance(config_name, str):
        config_obj = config[config_name]
    else:
        config_obj = config_name
        
    app.config.from_object(config_obj)
    config_obj.init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    
    # Configure Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.database import User
        return User.query.get(int(user_id))
    
    # Register Blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize monitoring
    start_monitoring()
    
    # Error handlers
    from app.main.errors import register_error_handlers
    register_error_handlers(app)
    
    return app