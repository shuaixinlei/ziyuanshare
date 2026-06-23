from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    login_manager.init_app(app)
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)
    
    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp)
    
    with app.app_context():
        db.create_all()
        from app.models import User, Course
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            from werkzeug.security import generate_password_hash
            admin = User(username='admin', email='admin@example.com', 
                         password_hash=generate_password_hash('admin123'), 
                         is_admin=True)
            db.session.add(admin)
            db.session.commit()
        if not Course.query.first():
            courses = [
                Course(name='高等数学', category='数学'),
                Course(name='线性代数', category='数学'),
                Course(name='概率论与数理统计', category='数学'),
                Course(name='大学英语', category='语言'),
                Course(name='计算机基础', category='计算机'),
                Course(name='数据结构', category='计算机'),
                Course(name='操作系统', category='计算机'),
                Course(name='数据库原理', category='计算机'),
                Course(name='管理学原理', category='管理'),
                Course(name='经济学原理', category='经济'),
            ]
            db.session.add_all(courses)
            db.session.commit()
    
    return app