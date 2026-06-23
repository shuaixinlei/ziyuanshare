import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_from_directory
from flask_login import current_user, login_required
from app import db
from app.models import Course, Material, DownloadRecord, User

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    categories = Course.query.with_entities(Course.category).distinct().all()
    categories = [c[0] for c in categories]
    
    courses_by_category = {}
    for category in categories:
        count = Course.query.filter_by(category=category).count()
        courses_by_category[category] = count
    
    recent_materials = Material.query.filter_by(is_approved=True).order_by(Material.upload_time.desc()).limit(6).all()
    
    top_contributors = User.query.filter_by(is_admin=False).order_by(User.points.desc()).limit(5).all()
    
    total_materials = Material.query.filter_by(is_approved=True).count()
    total_courses = Course.query.count()
    total_users = User.query.count()
    
    return render_template('main/index.html', 
                           categories=categories,
                           courses_by_category=courses_by_category,
                           recent_materials=recent_materials,
                           top_contributors=top_contributors,
                           total_materials=total_materials,
                           total_courses=total_courses,
                           total_users=total_users)

@bp.route('/category/<category_name>')
def category(category_name):
    courses = Course.query.filter_by(category=category_name).all()
    return render_template('main/category.html', 
                           category_name=category_name,
                           courses=courses)

@bp.route('/course/<int:course_id>')
def course(course_id):
    course = Course.query.get_or_404(course_id)
    materials = Material.query.filter_by(course_id=course_id, is_approved=True).order_by(Material.upload_time.desc())
    
    material_types = ['all', 'notes', 'exam']
    selected_type = request.args.get('type', 'all')
    
    if selected_type != 'all':
        materials = materials.filter_by(material_type=selected_type)
    
    materials = materials.all()
    
    return render_template('main/course.html', 
                           course=course,
                           materials=materials,
                           selected_type=selected_type)

@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    courses = Course.query.all()
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        course_id = request.form['course_id']
        material_type = request.form['material_type']
        
        if 'file' not in request.files:
            flash('请选择文件', 'danger')
            return redirect(url_for('main.upload'))
        
        file = request.files['file']
        
        if file.filename == '':
            flash('请选择文件', 'danger')
            return redirect(url_for('main.upload'))
        
        if file:
            from app import create_app
            app = create_app()
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            file_type = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'unknown'
            
            material = Material(
                title=title,
                description=description,
                file_path=filename,
                file_type=file_type,
                material_type=material_type,
                uploader_id=current_user.id,
                course_id=course_id
            )
            
            db.session.add(material)
            current_user.add_points(10)
            db.session.commit()
            
            flash('上传成功！已获得10积分', 'success')
            return redirect(url_for('main.index'))
    
    return render_template('main/upload.html', courses=courses)

@bp.route('/download/<int:material_id>')
def download(material_id):
    material = Material.query.get_or_404(material_id)
    
    if not material.is_approved:
        flash('该资料尚未审核通过', 'warning')
        return redirect(url_for('main.course', course_id=material.course_id))
    
    from app import create_app
    app = create_app()
    upload_folder = app.config['UPLOAD_FOLDER']
    
    material.download_count += 1
    
    if current_user.is_authenticated:
        record = DownloadRecord(user_id=current_user.id, material_id=material_id)
        db.session.add(record)
        
        if material.download_count % 10 == 0:
            material.uploader.add_points(5)
    
    db.session.commit()
    
    return send_from_directory(upload_folder, material.file_path, as_attachment=True)

@bp.route('/leaderboard')
def leaderboard():
    contributors = User.query.filter_by(is_admin=False).order_by(User.points.desc()).all()
    return render_template('main/leaderboard.html', contributors=contributors)

@bp.route('/search')
def search():
    keyword = request.args.get('keyword', '')
    materials = Material.query.filter(Material.title.contains(keyword), Material.is_approved == True).all()
    return render_template('main/search.html', materials=materials, keyword=keyword)

from werkzeug.utils import secure_filename