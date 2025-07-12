from flask import render_template, jsonify
from app.utils.monitoring import metrics_collector
import logging

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    """Registrar manejadores de errores globales"""
    
    @app.errorhandler(404)
    def not_found(error):
        """Manejar errores 404"""
        metrics_collector.increment_counter('http_errors_total', tags={'status': '404'})
        return render_template('index.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Manejar errores 500"""
        logger.error(f"Error interno del servidor: {error}")
        metrics_collector.increment_counter('http_errors_total', tags={'status': '500'})
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor. Por favor, intenta de nuevo más tarde.',
            'offline': True
        }), 500

    @app.errorhandler(503)
    def service_unavailable(error):
        """Manejar errores 503 - servicio no disponible"""
        metrics_collector.increment_counter('http_errors_total', tags={'status': '503'})
        return jsonify({
            'success': False,
            'error': 'Servicio temporalmente no disponible. Intente más tarde.'
        }), 503