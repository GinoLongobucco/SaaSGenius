import os
from dotenv import load_dotenv
from config.config import get_config, validate_environment

# Load environment variables
load_dotenv()

# Get centralized configuration
app_config = get_config()

class Config:
    SECRET_KEY = app_config.security.secret_key or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = app_config.database.database_url or 'sqlite:///saasgenius.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_SIZE = app_config.database.pool_size
    SQLALCHEMY_MAX_OVERFLOW = app_config.database.max_overflow
    SQLALCHEMY_POOL_TIMEOUT = app_config.database.pool_timeout
    SQLALCHEMY_POOL_RECYCLE = app_config.database.pool_recycle
    SQLALCHEMY_ECHO = app_config.database.echo
    
    # API configuration
    GROQ_API_KEY = app_config.api.groq_api_key
    HUGGINGFACE_API_KEY = app_config.api.huggingface_api_key
    
    # Analysis configuration
    MAX_ANALYSIS_LENGTH = 10000
    CACHE_TIMEOUT = app_config.cache.default_ttl
    
    # Logging configuration
    LOG_LEVEL = app_config.monitoring.log_level
    
    # Security configuration
    JWT_SECRET_KEY = app_config.security.jwt_secret_key
    JWT_ACCESS_TOKEN_EXPIRES = app_config.security.jwt_access_token_expires
    JWT_REFRESH_TOKEN_EXPIRES = app_config.security.jwt_refresh_token_expires
    
    # Rate limiting
    RATELIMIT_PER_MINUTE = app_config.security.rate_limit_per_minute
    RATELIMIT_PER_HOUR = app_config.security.rate_limit_per_hour
    
    # CORS
    CORS_ORIGINS = app_config.security.cors_origins or ['*']
    CORS_METHODS = app_config.security.cors_methods or ['GET', 'POST', 'PUT', 'DELETE']
    
    @staticmethod
    def init_app(app):
        """Initialize application with this configuration"""
        pass
    
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True
    
class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False
    
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_ECHO = True
    CACHE_TIMEOUT = 60  # 1 minute for testing
    
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

# Validate configuration on import
if not validate_environment():
    import logging
    logging.warning("Some critical configurations are missing. Check environment variables.")