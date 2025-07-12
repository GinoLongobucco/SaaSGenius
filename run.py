import os
from app import create_app
from config.settings import config
from config.config import get_config, validate_environment
from app.utils.monitoring import start_monitoring
from app.database import init_database, create_demo_user
import logging

# Validate configuration at startup
if not validate_environment():
    logging.warning("Algunas configuraciones críticas no están presentes. La aplicación puede no funcionar correctamente.")

# Create application
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

# Initialize database and demo user
with app.app_context():
    try:
        init_database()
        create_demo_user()
        logging.info("Base de datos y cuenta demo inicializadas correctamente")
    except Exception as e:
        logging.error(f"Error al inicializar la base de datos: {e}")

# Initialize monitoring system
app_config = get_config()
if app_config.monitoring.enabled:
    start_monitoring()
    logging.info("Sistema de monitoreo iniciado")

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') != 'production'
    
    logging.info(f"Iniciando SaaSGenius en puerto {port} (debug={debug})")
    logging.info("Cuenta demo disponible - Usuario: demo, Contraseña: demo123")
    app.run(debug=debug, host='0.0.0.0', port=port)