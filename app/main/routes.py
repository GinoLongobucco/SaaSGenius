from flask import render_template, request, jsonify, redirect
from flask_login import login_required, current_user
from app.main import bp
from app.database import get_user_projects, get_project_by_id, log_analytics_event
from models.unified_analyzer import UnifiedSaaSAnalyzer, analyze_project_description
from app.utils.monitoring import performance_monitor, metrics_collector
import logging
import json
import time

logger = logging.getLogger(__name__)

@bp.route('/')
@performance_monitor.monitor_endpoint('index')
def index():
    """Página principal"""
    # Check if user is authenticated and if there are query parameters
    edit_id = request.args.get('edit')
    view_id = request.args.get('view')
    
    # If there are edit/view parameters, stay on index page to handle them
    return render_template('index.html')

@bp.route('/dashboard')
@login_required
@performance_monitor.monitor_endpoint('dashboard')
def dashboard():
    """Dashboard del usuario"""
    # Get user's recent projects
    projects = get_user_projects(current_user.id, limit=10)
    
    # Parse analysis data for each project
    for project in projects:
        if project.analysis_data:
            try:
                project.parsed_analysis = json.loads(project.analysis_data)
            except json.JSONDecodeError:
                project.parsed_analysis = None
        else:
            project.parsed_analysis = None
    
    # Log dashboard visit
    log_analytics_event(
        current_user.id,
        'dashboard_visit',
        {'username': current_user.username},
        request.remote_addr,
        request.headers.get('User-Agent')
    )
    
    return render_template('dashboard.html', projects=projects, user=current_user)

@bp.route('/analysis')
@login_required
@performance_monitor.monitor_endpoint('analysis_view')
def analysis_view():
    """Página para mostrar análisis completo de un proyecto"""
    project_id = request.args.get('id')
    
    if not project_id:
        return redirect('/dashboard')
    
    # Verificar que el proyecto existe y pertenece al usuario
    project = get_project_by_id(int(project_id), current_user.id)
    
    if not project:
        return redirect('/dashboard')
    
    # Log analysis view
    log_analytics_event(
        current_user.id,
        'analysis_viewed',
        {'project_id': project_id, 'project_title': project.title},
        request.remote_addr,
        request.headers.get('User-Agent')
    )
    
    return render_template('analysis.html')

@bp.route('/analyze_project', methods=['POST'])
@performance_monitor.monitor_endpoint('analyze_project')
def analyze_project_route():
    """Analizar un proyecto"""
    try:
        # Obtener datos raw y decodificar manualmente
        raw_data = request.get_data()
        
        # Intentar decodificar con diferentes métodos
        try:
            # Primero intentar UTF-8 estándar
            json_str = raw_data.decode('utf-8')
        except UnicodeDecodeError:
            try:
                # Intentar con latin-1 y luego convertir
                json_str = raw_data.decode('latin-1')
            except UnicodeDecodeError:
                # Como último recurso, ignorar errores
                json_str = raw_data.decode('utf-8', errors='ignore')
        
        # Parsear JSON
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            # Fallback al método original
            data = request.get_json(force=True)
        
        if not data or 'description' not in data:
            return jsonify({
                'success': False,
                'error': 'No project description provided'
            }), 400
        
        description = data['description'].strip()
        
        if not description:
            return jsonify({
                'success': False,
                'error': 'Project description cannot be empty'
            }), 400
        
        if len(description) < 10:
            return jsonify({
                'success': False,
                'error': 'Project description is too short. Please provide more details.'
            }), 400
        
        # Incrementar contador de análisis
        if current_user.is_authenticated:
            metrics_collector.increment_counter('analysis_requests_total', 
                                               tags={'user_id': str(current_user.id)})
        
        start_time = time.time()
        
        # Initialize unified analyzer
        analyzer = UnifiedSaaSAnalyzer()
        
        # Analyze the project with unified model
        result = analyzer.analyze_project(description)
        
        # Registrar tiempo de análisis
        analysis_time = time.time() - start_time
        metrics_collector.record_histogram('analysis_duration_seconds', analysis_time)
        
        # Agregar tiempo de análisis al resultado
        result['analysis_time'] = round(analysis_time, 2)
        
        # Save project if user is authenticated
        if current_user.is_authenticated:
            try:
                from app.database import save_project
                # Obtener el título del proyecto desde analysis_metadata.suggested_name
                project_title = result.get('analysis_metadata', {}).get('suggested_name', 'Untitled Project')
                
                project_id = save_project(
                    user_id=current_user.id,
                    title=project_title,
                    description=description,
                    analysis_data=result
                )
                result['project_id'] = project_id
                
                # Log analysis event
                log_analytics_event(
                    current_user.id,
                    'project_analyzed',
                    {
                        'project_id': project_id,
                        'project_name': result.get('project_name'),
                        'description_length': len(description)
                    },
                    request.remote_addr,
                    request.headers.get('User-Agent')
                )
                
                logger.info(f"Project analysis saved for user {current_user.username}")
            except Exception as save_error:
                logger.error(f"Error saving project: {str(save_error)}")
                # Continue without saving - don't fail the analysis
        
        logger.info(f"Project analysis completed successfully")
        return jsonify({
            'success': True,
            'analysis': result
        })
        
    except Exception as e:
        logger.error(f"Error analyzing project: {str(e)}")
        metrics_collector.increment_counter('analysis_errors_total', 
                                           tags={'error_type': type(e).__name__})
        return jsonify({
            'success': False,
            'error': 'An error occurred while analyzing the project. Please try again.'
        }), 500

@bp.route('/health')
def health_check():
    """Endpoint de verificación de salud"""
    try:
        from app.utils.monitoring import health_checker
        health_status = health_checker.check_system_health()
        status_code = 200 if health_status['status'] == 'healthy' else 503
        return jsonify(health_status), status_code
    except Exception as e:
        logger.error(f'Error en health check: {e}')
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': time.time()
        }), 503

@bp.route('/metrics')
def metrics_endpoint():
    """Endpoint de métricas para Prometheus"""
    try:
        metrics = metrics_collector.export_metrics()
        return metrics, 200, {'Content-Type': 'application/json'}
    except Exception as e:
        logger.error(f'Error exportando métricas: {e}')
        return jsonify({'error': 'Error obteniendo métricas'}), 500

@bp.route('/performance')
@login_required
def performance_stats():
    """Estadísticas de rendimiento para el dashboard"""
    try:
        from app.utils.monitoring import health_checker
        metrics = metrics_collector.get_application_metrics()
        
        # Calcular estadísticas útiles
        stats = {
            'total_requests': sum(v for k, v in metrics.get('counters', {}).items() 
                                if 'requests_total' in k),
            'total_errors': sum(v for k, v in metrics.get('counters', {}).items() 
                              if 'errors_total' in k),
            'avg_response_time': 0,
            'system_health': health_checker.check_system_health()['status'],
            'uptime': metrics.get('system', {}).get('uptime_seconds', 0)
        }
        
        # Calcular tiempo promedio de respuesta
        histograms = metrics.get('histograms', {})
        for key, hist in histograms.items():
            if 'duration_seconds' in key:
                stats['avg_response_time'] = hist.get('avg', 0)
                break
        
        return jsonify(stats)
    except Exception as e:
        logger.error(f'Error obteniendo estadísticas: {e}')
        return jsonify({'error': 'Error obteniendo estadísticas'}), 500