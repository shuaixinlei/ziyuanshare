from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    points = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    materials = db.relationship('Material', backref='uploader', lazy='dynamic')
    downloads = db.relationship('DownloadRecord', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)
    
    def add_points(self, points):
        self.points += points
    
    def __repr__(self):
        return f'<User {self.username}>'

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    
    materials = db.relationship('Material', backref='course', lazy='dynamic')
    
    def __repr__(self):
        return f'<Course {self.name}>'

class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    file_path = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(20), nullable=False)
    material_type = db.Column(db.String(20), nullable=False)
    uploader_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
    download_count = db.Column(db.Integer, default=0)
    is_approved = db.Column(db.Boolean, default=True)
    
    downloads = db.relationship('DownloadRecord', backref='material', lazy='dynamic')
    
    def __repr__(self):
        return f'<Material {self.title}>'

class DownloadRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    material_id = db.Column(db.Integer, db.ForeignKey('material.id'))
    download_time = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<DownloadRecord {self.user_id} - {self.material_id}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))