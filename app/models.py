from app.database import db, User, Project, AnalyticsEvent

# Re-exportar los modelos para facilitar las importaciones
__all__ = ['User', 'Project', 'AnalyticsEvent']