import asyncio
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional, Callable, List
import logging

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class AnalysisTask:
    id: str
    description: str
    status: TaskStatus
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: float = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    progress: float = 0.0
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()

class AsyncAnalysisManager:
    """Gestor de análisis asíncronos"""
    
    def __init__(self, max_workers: int = 4, max_queue_size: int = 100):
        self.max_workers = max_workers
        self.max_queue_size = max_queue_size
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.tasks: Dict[str, AnalysisTask] = {}
        self.lock = threading.RLock()
        self.cleanup_interval = 3600  # 1 hora
        self.max_task_age = 86400  # 24 horas
        
        # Iniciar hilo de limpieza
        self.cleanup_thread = threading.Thread(target=self._cleanup_old_tasks, daemon=True)
        self.cleanup_thread.start()
        
        logger.info(f"AsyncAnalysisManager iniciado con {max_workers} workers")
    
    def submit_task(self, task_func: Callable, description: str, *args, **kwargs) -> str:
        """Envía una tarea para análisis asíncrono"""
        with self.lock:
            if len(self.tasks) >= self.max_queue_size:
                raise RuntimeError("Cola de tareas llena")
            
            task_id = str(uuid.uuid4())
            task = AnalysisTask(
                id=task_id,
                description=description,
                status=TaskStatus.PENDING
            )
            
            self.tasks[task_id] = task
            
            # Enviar al executor
            future = self.executor.submit(self._execute_task, task_id, task_func, *args, **kwargs)
            
            logger.info(f"Tarea {task_id} enviada: {description}")
            return task_id
    
    def _execute_task(self, task_id: str, task_func: Callable, *args, **kwargs):
        """Ejecuta una tarea y actualiza su estado"""
        try:
            with self.lock:
                if task_id not in self.tasks:
                    return
                
                task = self.tasks[task_id]
                task.status = TaskStatus.PROCESSING
                task.started_at = time.time()
            
            logger.info(f"Iniciando ejecución de tarea {task_id}")
            
            # Ejecutar la función
            result = task_func(*args, **kwargs)
            
            with self.lock:
                if task_id in self.tasks:
                    task = self.tasks[task_id]
                    task.status = TaskStatus.COMPLETED
                    task.result = result
                    task.completed_at = time.time()
                    task.progress = 100.0
            
            logger.info(f"Tarea {task_id} completada exitosamente")
            
        except Exception as e:
            logger.error(f"Error en tarea {task_id}: {str(e)}")
            
            with self.lock:
                if task_id in self.tasks:
                    task = self.tasks[task_id]
                    task.status = TaskStatus.FAILED
                    task.error = str(e)
                    task.completed_at = time.time()
    
    def get_task_status(self, task_id: str) -> Optional[AnalysisTask]:
        """Obtiene el estado de una tarea"""
        with self.lock:
            return self.tasks.get(task_id)
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancela una tarea (solo si está pendiente)"""
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            if task.status == TaskStatus.PENDING:
                task.status = TaskStatus.CANCELLED
                task.completed_at = time.time()
                logger.info(f"Tarea {task_id} cancelada")
                return True
            
            return False
    
    def get_all_tasks(self) -> List[AnalysisTask]:
        """Obtiene todas las tareas"""
        with self.lock:
            return list(self.tasks.values())
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de la cola"""
        with self.lock:
            status_counts = {}
            for task in self.tasks.values():
                status = task.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
            
            return {
                'total_tasks': len(self.tasks),
                'max_queue_size': self.max_queue_size,
                'active_workers': self.max_workers,
                'status_breakdown': status_counts
            }
    
    def _cleanup_old_tasks(self):
        """Hilo de limpieza para eliminar tareas antiguas"""
        while True:
            try:
                current_time = time.time()
                
                with self.lock:
                    old_task_ids = [
                        task_id for task_id, task in self.tasks.items()
                        if (current_time - task.created_at) > self.max_task_age
                        and task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
                    ]
                    
                    for task_id in old_task_ids:
                        del self.tasks[task_id]
                    
                    if old_task_ids:
                        logger.info(f"Limpiadas {len(old_task_ids)} tareas antiguas")
                
                time.sleep(self.cleanup_interval)
                
            except Exception as e:
                logger.error(f"Error en limpieza de tareas: {e}")
                time.sleep(60)  # Esperar 1 minuto antes de reintentar
    
    def shutdown(self):
        """Cierra el gestor y espera a que terminen las tareas"""
        logger.info("Cerrando AsyncAnalysisManager...")
        self.executor.shutdown(wait=True)
        logger.info("AsyncAnalysisManager cerrado")

# Instancia global del gestor
async_manager = AsyncAnalysisManager()