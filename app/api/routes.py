from flask import request, jsonify
from flask_login import login_required, current_user
from app.api import bp
from app.database import get_user_projects, get_project_by_id, update_project, delete_project, log_analytics_event
from app.utils.monitoring import performance_monitor, metrics_collector
from models.unified_analyzer import UnifiedSaaSAnalyzer
import logging
import asyncio
import json
from datetime import datetime

logger = logging.getLogger(__name__)

# Instancia global del analizador unificado
unified_analyzer = UnifiedSaaSAnalyzer()

@bp.route('/projects', methods=['GET'])
@login_required
@performance_monitor.monitor_endpoint('api_get_projects')
def get_projects():
    """Get user's projects with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        offset = (page - 1) * limit
        
        projects = get_user_projects(current_user.id, limit=limit, offset=offset)
        
        return jsonify({
            'success': True,
            'projects': [project.to_dict() for project in projects],
            'page': page,
            'limit': limit
        })
    except Exception as e:
        logger.error(f"Error getting projects: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to get projects'}), 500

@bp.route('/projects/<int:project_id>', methods=['GET'])
@login_required
def get_project(project_id):
    """Get a specific project"""
    try:
        project = get_project_by_id(project_id, current_user.id)
        
        if not project:
            return jsonify({'success': False, 'error': 'Project not found'}), 404
        
        return jsonify({
            'success': True,
            'project': project.to_dict()
        })
    except Exception as e:
        logger.error(f"Error getting project: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to get project'}), 500

@bp.route('/projects/<int:project_id>', methods=['PUT'])
@login_required
@performance_monitor.monitor_endpoint('api_update_project')
def update_project_route(project_id):
    """Update a project"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Validate allowed fields
        allowed_fields = ['title', 'description', 'is_favorite', 'tags']
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        if not update_data:
            return jsonify({'success': False, 'error': 'No valid fields to update'}), 400
        
        success = update_project(project_id, current_user.id, **update_data)
        
        if not success:
            return jsonify({'success': False, 'error': 'Project not found'}), 404
        
        # Log update event
        log_analytics_event(
            current_user.id,
            'project_updated',
            {'project_id': project_id, 'updated_fields': list(update_data.keys())},
            request.remote_addr,
            request.headers.get('User-Agent')
        )
        
        return jsonify({'success': True, 'message': 'Project updated successfully'})
    except Exception as e:
        logger.error(f"Error updating project: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to update project'}), 500

@bp.route('/projects/<int:project_id>', methods=['DELETE'])
@login_required
@performance_monitor.monitor_endpoint('api_delete_project')
def delete_project_route(project_id):
    """Delete a project"""
    try:
        success = delete_project(project_id, current_user.id)
        
        if not success:
            return jsonify({'success': False, 'error': 'Project not found'}), 404
        
        metrics_collector.increment_counter('project_deletions_total')
        
        # Log delete event
        log_analytics_event(
            current_user.id,
            'project_deleted',
            {'project_id': project_id},
            request.remote_addr,
            request.headers.get('User-Agent')
        )
        
        return jsonify({'success': True, 'message': 'Project deleted successfully'})
    except Exception as e:
        logger.error(f"Error deleting project: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to delete project'}), 500

# ============================================================================
# NUEVOS ENDPOINTS DE ANÁLISIS OPTIMIZADO
# ============================================================================

@bp.route('/analyze/optimized', methods=['POST'])
@login_required
@performance_monitor.monitor_endpoint('api_optimized_analysis')
def analyze_project_optimized():
    """Análisis optimizado con búsqueda web, prompts avanzados y stack dinámico"""
    try:
        data = request.get_json()
        
        if not data or 'description' not in data:
            return jsonify({
                'success': False, 
                'error': 'Project description is required'
            }), 400
        
        description = data['description']
        analysis_type = data.get('analysis_type', 'complete')  # complete, market, tech, executive, roadmap
        
        # Validar tipo de análisis
        valid_types = ['complete', 'market', 'tech', 'executive', 'roadmap']
        if analysis_type not in valid_types:
            return jsonify({
                'success': False,
                'error': f'Invalid analysis type. Must be one of: {", ".join(valid_types)}'
            }), 400
        
        # Ejecutar análisis optimizado de forma asíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            analysis_result = loop.run_until_complete(
                unified_analyzer.analyze_project(description)
            )
        finally:
            loop.close()
        
        # Log del evento de análisis
        log_analytics_event(
            current_user.id,
            'optimized_analysis_completed',
            {
                'analysis_type': analysis_type,
                'description_length': len(description),
                'optimization_version': '3.0'
            },
            request.remote_addr,
            request.headers.get('User-Agent')
        )
        
        metrics_collector.increment_counter('optimized_analysis_total')
        
        return jsonify({
            'success': True,
            'analysis': analysis_result,
            'analysis_type': analysis_type,
            'timestamp': analysis_result.get('analysis_metadata', {}).get('timestamp')
        })
        
    except Exception as e:
        logger.error(f"Error in optimized analysis: {str(e)}")
        metrics_collector.increment_counter('optimized_analysis_errors_total')
        return jsonify({
            'success': False, 
            'error': 'Failed to complete optimized analysis',
            'details': str(e)
        }), 500

@bp.route('/analyze/market-intelligence', methods=['POST'])
@login_required
@performance_monitor.monitor_endpoint('api_market_intelligence')
def get_market_intelligence():
    """Obtiene inteligencia de mercado en tiempo real"""
    try:
        data = request.get_json()
        
        if not data or 'description' not in data:
            return jsonify({
                'success': False,
                'error': 'Project description is required'
            }), 400
        
        description = data['description']
        
        # Ejecutar solo análisis de mercado
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            market_analysis = loop.run_until_complete(
                unified_analyzer.analyze_project(description)
            )
        finally:
            loop.close()
        
        # Extraer solo datos de mercado
        market_data = market_analysis.get('market_analysis', {})
        metadata = market_analysis.get('analysis_metadata', {})
        
        return jsonify({
            'success': True,
            'market_intelligence': market_data,
            'confidence_score': metadata.get('web_search_confidence', 0.0),
            'industry_detected': metadata.get('industry_detected'),
            'keywords_extracted': metadata.get('keywords_extracted', []),
            'timestamp': metadata.get('timestamp')
        })
        
    except Exception as e:
        logger.error(f"Error in market intelligence: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get market intelligence',
            'details': str(e)
        }), 500

@bp.route('/analyze/tech-stack-recommendation', methods=['POST'])
@login_required
@performance_monitor.monitor_endpoint('api_tech_stack_recommendation')
def get_tech_stack_recommendation():
    """Obtiene recomendación dinámica de stack tecnológico"""
    try:
        data = request.get_json()
        
        if not data or 'description' not in data:
            return jsonify({
                'success': False,
                'error': 'Project description is required'
            }), 400
        
        description = data['description']
        
        # Ejecutar solo análisis de stack tecnológico
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            tech_analysis = loop.run_until_complete(
                unified_analyzer.analyze_project(description)
            )
        finally:
            loop.close()
        
        # Extraer datos de stack tecnológico
        tech_data = tech_analysis.get('tech_stack', {})
        metadata = tech_analysis.get('analysis_metadata', {})
        
        return jsonify({
            'success': True,
            'tech_stack_recommendation': tech_data,
            'industry_context': metadata.get('industry_detected'),
            'scale_context': metadata.get('scale_detected'),
            'timestamp': metadata.get('timestamp')
        })
        
    except Exception as e:
        logger.error(f"Error in tech stack recommendation: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get tech stack recommendation',
            'details': str(e)
        }), 500

@bp.route('/analyze/executive-summary', methods=['POST'])
@login_required
@performance_monitor.monitor_endpoint('api_executive_summary')
def get_executive_summary():
    """Genera resumen ejecutivo optimizado"""
    try:
        data = request.get_json()
        
        if not data or 'description' not in data:
            return jsonify({
                'success': False,
                'error': 'Project description is required'
            }), 400
        
        description = data['description']
        
        # Ejecutar análisis de resumen ejecutivo
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            executive_analysis = loop.run_until_complete(
                unified_analyzer.analyze_project(description)
            )
        finally:
            loop.close()
        
        # Extraer datos de resumen ejecutivo
        executive_data = executive_analysis.get('executive_summary', {})
        metadata = executive_analysis.get('analysis_metadata', {})
        
        return jsonify({
            'success': True,
            'executive_summary': executive_data,
            'confidence_level': metadata.get('web_search_confidence', 0.0),
            'analysis_context': {
                'industry': metadata.get('industry_detected'),
                'scale': metadata.get('scale_detected'),
                'keywords': metadata.get('keywords_extracted', [])
            },
            'timestamp': metadata.get('timestamp')
        })
        
    except Exception as e:
        logger.error(f"Error in executive summary: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate executive summary',
            'details': str(e)
        }), 500

@bp.route('/analyze/development-roadmap', methods=['POST'])
@login_required
@performance_monitor.monitor_endpoint('api_development_roadmap')
def get_development_roadmap():
    """Genera roadmap de desarrollo optimizado"""
    try:
        data = request.get_json()
        
        if not data or 'description' not in data:
            return jsonify({
                'success': False,
                'error': 'Project description is required'
            }), 400
        
        description = data['description']
        
        # Ejecutar análisis de roadmap
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            roadmap_analysis = loop.run_until_complete(
                unified_analyzer.analyze_project(description)
            )
        finally:
            loop.close()
        
        # Extraer datos de roadmap
        roadmap_data = roadmap_analysis.get('development_roadmap', {})
        metadata = roadmap_analysis.get('analysis_metadata', {})
        
        return jsonify({
            'success': True,
            'development_roadmap': roadmap_data,
            'project_context': {
                'industry': metadata.get('industry_detected'),
                'scale': metadata.get('scale_detected'),
                'estimated_timeline': roadmap_data.get('estimated_timeline')
            },
            'timestamp': metadata.get('timestamp')
        })
        
    except Exception as e:
        logger.error(f"Error in development roadmap: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate development roadmap',
            'details': str(e)
        }), 500

@bp.route('/analyze/health-check', methods=['GET'])
@login_required
def analyzer_health_check():
    """Verifica el estado del analizador optimizado"""
    try:
        health_status = {
            'analyzer_status': 'operational',
            'web_search_available': hasattr(unified_analyzer, 'web_search'),
            'prompt_engineering_available': hasattr(unified_analyzer, 'prompt_engineer'),
            'tech_analyzer_available': hasattr(unified_analyzer, 'tech_analyzer'),
            'optimization_version': '3.0',
            'timestamp': json.dumps(datetime.now(), default=str)
        }
        
        return jsonify({
            'success': True,
            'health': health_status
        })
        
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Health check failed',
            'details': str(e)
        }), 500