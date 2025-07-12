# Sistema de Monitoreo Unificado - Versión Final Optimizada
import psutil
import threading
import time
import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from functools import wraps
from collections import defaultdict, deque
import json
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class MetricData:
    """Estructura para datos de métricas"""
    value: float
    timestamp: float
    tags: Dict[str, str] = field(default_factory=dict)

@dataclass
class AlertRule:
    """Regla de alerta"""
    name: str
    condition: Callable[[float], bool]
    message: str
    cooldown: int = 300  # 5 minutos
    last_triggered: float = 0

@dataclass
class ProgressStep:
    """Paso de progreso para análisis complejos"""
    name: str
    description: str
    weight: float = 1.0
    completed: bool = False
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    error: Optional[str] = None

class MetricsCollector:
    """Recolector de métricas del sistema"""
    
    def __init__(self):
        self.metrics = defaultdict(lambda: deque(maxlen=1000))
        self.counters = defaultdict(int)
        self.gauges = defaultdict(float)
        self.histograms = defaultdict(list)
        self._lock = threading.RLock()
        
    def record_metric(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Registra una métrica"""
        with self._lock:
            metric = MetricData(value, time.time(), tags or {})
            self.metrics[name].append(metric)
    
    def increment_counter(self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None):
        """Incrementa un contador"""
        with self._lock:
            self.counters[name] += value
            self.record_metric(f"{name}_total", self.counters[name], tags)
    
    def set_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Establece un gauge"""
        with self._lock:
            self.gauges[name] = value
            self.record_metric(name, value, tags)
    
    def record_histogram(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Registra un valor en histograma"""
        with self._lock:
            self.histograms[name].append(value)
            # Keep only the last 1000 values
            if len(self.histograms[name]) > 1000:
                self.histograms[name] = self.histograms[name][-1000:]
            self.record_metric(name, value, tags)
    
    def get_system_metrics(self) -> Dict[str, float]:
        """Obtiene métricas del sistema"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            metrics = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used_gb': memory.used / (1024**3),
                'memory_available_gb': memory.available / (1024**3),
                'disk_percent': disk.percent,
                'disk_used_gb': disk.used / (1024**3),
                'disk_free_gb': disk.free / (1024**3)
            }
            
            # Record metrics
            for name, value in metrics.items():
                self.set_gauge(f"system_{name}", value)
            
            return metrics
        except Exception as e:
            logger.error(f"Error obteniendo métricas del sistema: {e}")
            return {}
    
    def get_metric_summary(self, name: str, window_seconds: int = 300) -> Dict[str, float]:
        """Obtiene resumen de una métrica en ventana de tiempo"""
        with self._lock:
            if name not in self.metrics:
                return {}
            
            cutoff_time = time.time() - window_seconds
            recent_values = [
                m.value for m in self.metrics[name] 
                if m.timestamp >= cutoff_time
            ]
            
            if not recent_values:
                return {}
            
            return {
                'count': len(recent_values),
                'min': min(recent_values),
                'max': max(recent_values),
                'avg': sum(recent_values) / len(recent_values),
                'latest': recent_values[-1]
            }

class PerformanceMonitor:
    """Monitor de rendimiento para funciones y endpoints"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        self.active_requests = defaultdict(int)
        self.request_times = defaultdict(list)
        self.error_counts = defaultdict(int)
        self._lock = threading.RLock()
    
    def monitor_function(self, function_name: str):
        """Decorador para monitorear funciones"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                
                with self._lock:
                    self.active_requests[function_name] += 1
                
                try:
                    result = func(*args, **kwargs)
                    
                    # Record successful execution time
                    execution_time = time.time() - start_time
                    self.metrics.record_histogram(
                        f"function_duration_{function_name}", 
                        execution_time,
                        {'status': 'success'}
                    )
                    
                    return result
                    
                except Exception as e:
                    # Record error
                    execution_time = time.time() - start_time
                    with self._lock:
                        self.error_counts[function_name] += 1
                    
                    self.metrics.increment_counter(
                        f"function_errors_{function_name}",
                        tags={'error_type': type(e).__name__}
                    )
                    
                    self.metrics.record_histogram(
                        f"function_duration_{function_name}", 
                        execution_time,
                        {'status': 'error'}
                    )
                    
                    raise
                    
                finally:
                    with self._lock:
                        self.active_requests[function_name] -= 1
            
            return wrapper
        return decorator
    
    def monitor_endpoint(self, endpoint: str, method: str = 'GET'):
        """Decorador para monitorear endpoints"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                endpoint_key = f"{method}_{endpoint}"
                
                with self._lock:
                    self.active_requests[endpoint_key] += 1
                
                try:
                    result = func(*args, **kwargs)
                    
                    # Record response time
                    response_time = time.time() - start_time
                    self.metrics.record_histogram(
                        f"endpoint_response_time", 
                        response_time,
                        {'endpoint': endpoint, 'method': method, 'status': 'success'}
                    )
                    
                    self.metrics.increment_counter(
                        f"endpoint_requests",
                        tags={'endpoint': endpoint, 'method': method, 'status': 'success'}
                    )
                    
                    return result
                    
                except Exception as e:
                    # Record endpoint error
                    response_time = time.time() - start_time
                    with self._lock:
                        self.error_counts[endpoint_key] += 1
                    
                    self.metrics.increment_counter(
                        f"endpoint_requests",
                        tags={'endpoint': endpoint, 'method': method, 'status': 'error'}
                    )
                    
                    self.metrics.record_histogram(
                        f"endpoint_response_time", 
                        response_time,
                        {'endpoint': endpoint, 'method': method, 'status': 'error'}
                    )
                    
                    raise
                    
                finally:
                    with self._lock:
                        self.active_requests[endpoint_key] -= 1
            
            return wrapper
        return decorator
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Obtiene resumen de rendimiento"""
        with self._lock:
            return {
                'active_requests': dict(self.active_requests),
                'error_counts': dict(self.error_counts),
                'total_active': sum(self.active_requests.values()),
                'total_errors': sum(self.error_counts.values())
            }

class ProgressTracker:
    """Tracker de progreso para análisis complejos"""
    
    def __init__(self, task_id: str, steps: List[ProgressStep]):
        self.task_id = task_id
        self.steps = {step.name: step for step in steps}
        self.current_step = None
        self.start_time = time.time()
        self.end_time = None
        self.total_weight = sum(step.weight for step in steps)
        self._lock = threading.RLock()
    
    def start_step(self, step_name: str):
        """Inicia un paso"""
        with self._lock:
            if step_name in self.steps:
                self.current_step = step_name
                self.steps[step_name].start_time = time.time()
                logger.info(f"Iniciando paso: {step_name}")
    
    def complete_step(self, step_name: str, error: Optional[str] = None):
        """Completa un paso"""
        with self._lock:
            if step_name in self.steps:
                step = self.steps[step_name]
                step.completed = True
                step.end_time = time.time()
                step.error = error
                
                if error:
                    logger.error(f"Error en paso {step_name}: {error}")
                else:
                    logger.info(f"Completado paso: {step_name}")
    
    def get_progress(self) -> Dict[str, Any]:
        """Obtiene progreso actual"""
        with self._lock:
            completed_weight = sum(
                step.weight for step in self.steps.values() 
                if step.completed and not step.error
            )
            
            progress_percent = (completed_weight / self.total_weight) * 100
            
            return {
                'task_id': self.task_id,
                'progress_percent': progress_percent,
                'current_step': self.current_step,
                'completed_steps': len([s for s in self.steps.values() if s.completed]),
                'total_steps': len(self.steps),
                'elapsed_time': time.time() - self.start_time,
                'steps': {
                    name: {
                        'completed': step.completed,
                        'error': step.error,
                        'duration': step.end_time - step.start_time if step.end_time and step.start_time else None
                    }
                    for name, step in self.steps.items()
                }
            }
    
    def is_completed(self) -> bool:
        """Verifica si el tracking está completado"""
        return all(step.completed for step in self.steps.values())
    
    def has_errors(self) -> bool:
        """Verifica si hay errores"""
        return any(step.error for step in self.steps.values())

class HealthChecker:
    """Verificador de salud del sistema"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        self.thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_percent': 90.0,
            'response_time_ms': 5000.0
        }
    
    def check_health(self) -> Dict[str, Any]:
        """Verifica salud del sistema"""
        health_status = {
            'status': 'healthy',
            'checks': {},
            'timestamp': time.time()
        }
        
        try:
            # Verificar métricas del sistema
            system_metrics = self.metrics.get_system_metrics()
            
            for metric, threshold in self.thresholds.items():
                if metric in system_metrics:
                    value = system_metrics[metric]
                    is_healthy = value < threshold
                    
                    health_status['checks'][metric] = {
                        'status': 'pass' if is_healthy else 'fail',
                        'value': value,
                        'threshold': threshold
                    }
                    
                    if not is_healthy:
                        health_status['status'] = 'unhealthy'
            
            # Verificar tiempo de respuesta promedio
            response_time_summary = self.metrics.get_metric_summary('endpoint_response_time')
            if response_time_summary:
                avg_response_time = response_time_summary.get('avg', 0) * 1000  # a ms
                is_healthy = avg_response_time < self.thresholds['response_time_ms']
                
                health_status['checks']['response_time'] = {
                    'status': 'pass' if is_healthy else 'fail',
                    'value': avg_response_time,
                    'threshold': self.thresholds['response_time_ms']
                }
                
                if not is_healthy:
                    health_status['status'] = 'unhealthy'
            
        except Exception as e:
            logger.error(f"Error en verificación de salud: {e}")
            health_status['status'] = 'error'
            health_status['error'] = str(e)
        
        return health_status
    
    def set_threshold(self, metric: str, threshold: float):
        """Establece umbral para métrica"""
        self.thresholds[metric] = threshold

class AlertManager:
    """Gestor de alertas"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        self.rules = {}
        self.handlers = []
        self.alert_log_file = 'logs/alerts.log'
        
        # Crear directorio de logs si no existe
        os.makedirs(os.path.dirname(self.alert_log_file), exist_ok=True)
        
        # Configurar logging de alertas
        self.alert_logger = logging.getLogger('alerts')
        handler = logging.FileHandler(self.alert_log_file)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.alert_logger.addHandler(handler)
        self.alert_logger.setLevel(logging.INFO)
        
        # Reglas predefinidas
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """Configura reglas de alerta predefinidas"""
        self.add_rule(AlertRule(
            name='high_cpu',
            condition=lambda x: x > 80,
            message='CPU usage is above 80%: {value}%'
        ))
        
        self.add_rule(AlertRule(
            name='high_memory',
            condition=lambda x: x > 85,
            message='Memory usage is above 85%: {value}%'
        ))
        
        self.add_rule(AlertRule(
            name='high_error_rate',
            condition=lambda x: x > 10,
            message='Error rate is above 10 errors/minute: {value}'
        ))
    
    def add_rule(self, rule: AlertRule):
        """Agrega regla de alerta"""
        self.rules[rule.name] = rule
    
    def add_handler(self, handler: Callable[[str, str], None]):
        """Agrega manejador de alertas"""
        self.handlers.append(handler)
    
    def check_alerts(self):
        """Verifica y dispara alertas"""
        current_time = time.time()
        
        # Obtener métricas actuales
        system_metrics = self.metrics.get_system_metrics()
        
        for rule_name, rule in self.rules.items():
            # Verificar cooldown
            if current_time - rule.last_triggered < rule.cooldown:
                continue
            
            # Verificar condición según el tipo de regla
            value = None
            if rule_name == 'high_cpu':
                value = system_metrics.get('cpu_percent')
            elif rule_name == 'high_memory':
                value = system_metrics.get('memory_percent')
            elif rule_name == 'high_error_rate':
                # Calcular tasa de errores por minuto
                error_summary = self.metrics.get_metric_summary('endpoint_requests', 60)
                if error_summary:
                    value = error_summary.get('count', 0)
            
            if value is not None and rule.condition(value):
                self._trigger_alert(rule, value)
                rule.last_triggered = current_time
    
    def _trigger_alert(self, rule: AlertRule, value: float):
        """Dispara una alerta"""
        message = rule.message.format(value=value)
        
        # Log de alerta
        self.alert_logger.warning(f"ALERT: {rule.name} - {message}")
        
        # Ejecutar manejadores
        for handler in self.handlers:
            try:
                handler(rule.name, message)
            except Exception as e:
                logger.error(f"Error en manejador de alerta: {e}")

class MonitoringSystem:
    """Sistema de monitoreo unificado"""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.performance_monitor = PerformanceMonitor(self.metrics_collector)
        self.health_checker = HealthChecker(self.metrics_collector)
        self.alert_manager = AlertManager(self.metrics_collector)
        self.progress_trackers = {}
        
        self._monitoring_thread = None
        self._stop_monitoring = threading.Event()
        
    def start_monitoring(self, interval: int = 30):
        """Inicia monitoreo en background"""
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            logger.warning("Monitoreo ya está ejecutándose")
            return
        
        self._stop_monitoring.clear()
        self._monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval,),
            daemon=True
        )
        self._monitoring_thread.start()
        logger.info(f"Monitoreo iniciado con intervalo de {interval}s")
    
    def stop_monitoring(self):
        """Detiene monitoreo"""
        self._stop_monitoring.set()
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=5)
        logger.info("Monitoreo detenido")
    
    def _monitoring_loop(self, interval: int):
        """Loop principal de monitoreo"""
        while not self._stop_monitoring.wait(interval):
            try:
                # Recolectar métricas del sistema
                self.metrics_collector.get_system_metrics()
                
                # Verificar alertas
                self.alert_manager.check_alerts()
                
            except Exception as e:
                logger.error(f"Error en loop de monitoreo: {e}")
    
    def create_progress_tracker(self, task_id: str, steps: List[ProgressStep]) -> ProgressTracker:
        """Crea un tracker de progreso"""
        tracker = ProgressTracker(task_id, steps)
        self.progress_trackers[task_id] = tracker
        return tracker
    
    def get_progress_tracker(self, task_id: str) -> Optional[ProgressTracker]:
        """Obtiene un tracker de progreso"""
        return self.progress_trackers.get(task_id)
    
    def remove_progress_tracker(self, task_id: str):
        """Remueve un tracker de progreso"""
        self.progress_trackers.pop(task_id, None)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtiene estado completo del sistema"""
        return {
            'health': self.health_checker.check_health(),
            'performance': self.performance_monitor.get_performance_summary(),
            'metrics_summary': {
                'total_metrics': len(self.metrics_collector.metrics),
                'total_counters': len(self.metrics_collector.counters),
                'total_gauges': len(self.metrics_collector.gauges)
            },
            'active_trackers': len(self.progress_trackers),
            'monitoring_active': self._monitoring_thread and self._monitoring_thread.is_alive()
        }

# Instancia global del sistema de monitoreo
monitoring_system = MonitoringSystem()
metrics_collector = monitoring_system.metrics_collector
performance_monitor = monitoring_system.performance_monitor
health_checker = monitoring_system.health_checker
alert_manager = monitoring_system.alert_manager

# Función para iniciar monitoreo
def start_monitoring(interval: int = 30):
    """Inicia el sistema de monitoreo"""
    monitoring_system.start_monitoring(interval)

# Función para detener monitoreo
def stop_monitoring():
    """Detiene el sistema de monitoreo"""
    monitoring_system.stop_monitoring()

# Funciones de compatibilidad
def get_system_metrics() -> Dict[str, float]:
    """Función de compatibilidad para obtener métricas del sistema"""
    return metrics_collector.get_system_metrics()

def get_health_status() -> Dict[str, Any]:
    """Función de compatibilidad para obtener estado de salud"""
    return health_checker.check_health()