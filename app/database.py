from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    subscription_type = db.Column(db.String(20), default='free')
    last_login = db.Column(db.DateTime)
    projects = db.relationship('Project', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def is_premium(self):
        return self.subscription_type in ['premium', 'pro']

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    analysis_data = db.Column(db.Text)
    is_favorite = db.Column(db.Boolean, default=False)
    tags = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert project to dictionary for JSON serialization"""
        analysis_data = None
        if self.analysis_data:
            try:
                analysis_data = json.loads(self.analysis_data)
            except json.JSONDecodeError:
                analysis_data = None
        
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'analysis_data': analysis_data,
            'is_favorite': self.is_favorite,
            'tags': self.tags,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

def get_project_by_id(project_id, user_id):
    """Get a single project by its ID and user ID"""
    return Project.query.filter_by(id=project_id, user_id=user_id).first()

def check_project_ownership(project_id, user_id):
    """Check if a user owns a specific project"""
    return Project.query.filter_by(id=project_id, user_id=user_id).count() > 0

def count_user_projects(user_id):
    """Count total number of projects for a user"""
    return Project.query.filter_by(user_id=user_id).count()

def get_user_projects(user_id, limit=10, offset=0):
    """Get user projects with pagination"""
    return Project.query.filter_by(user_id=user_id).order_by(Project.updated_at.desc()).limit(limit).offset(offset).all()

def save_project(user_id, title, description, analysis_data, tags=None):
    """Save a new project analysis"""
    project = Project(
        user_id=user_id,
        title=title,
        description=description,
        analysis_data=json.dumps(analysis_data),
        tags=tags
    )
    db.session.add(project)
    db.session.commit()
    return project.id



def update_project(project_id, user_id, **kwargs):
    """Update a project (with user verification)"""
    project = get_project_by_id(project_id, user_id)
    if project:
        for key, value in kwargs.items():
            if hasattr(project, key):
                setattr(project, key, value)
        project.updated_at = datetime.utcnow()
        db.session.commit()
        return True
    return False

def delete_project(project_id, user_id):
    """Delete a project (with user verification)"""
    project = get_project_by_id(project_id, user_id)
    if project:
        db.session.delete(project)
        db.session.commit()
        return True
    return False

class Analytics(db.Model):
    __tablename__ = 'analytics'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_type = db.Column(db.String(50), nullable=False)
    event_data = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def log_analytics_event(user_id, event_type, event_data=None, ip_address=None, user_agent=None):
    """Log an analytics event"""
    event = Analytics(
        user_id=user_id,
        event_type=event_type,
        event_data=json.dumps(event_data),
        ip_address=ip_address,
        user_agent=user_agent
    )
    db.session.add(event)
    db.session.commit()

if __name__ == '__main__':
    init_database()
    create_demo_user()