import os
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import User, Course, Material

bp = Blueprint('admin', __name__)

def is_admin():
    return current_user.is_authenticated and current_user.is_admin

@bp.route('/admin')
@login_required
def admin_dashboard():
    if not is_admin():
        flash('无权访问', 'danger')
        return redirect(url_for('main.index'))
    
    total_users = User.query.count()
    total_materials = Material.query.count()
    total_courses = Course.query.count()
    pending_materials = Material.query.filter_by(is_approved=False).count()
    
    return render_template('admin/dashboard.html',
                           total_users=total_users,
                           total_materials=total_materials,
                           total_courses=total_courses,
                           pending_materials=pending_materials)

@bp.route('/admin/users')
@login_required
def manage_users():
    if not is_admin():
        flash('无权访问', 'danger')
        return redirect(url_for('main.index'))
    
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@bp.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not is_admin():
        flash('无权访问', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        user.is_admin = request.form.get('is_admin') == 'on'
        
        db.session.commit()
        flash('用户信息已更新', 'success')
        return redirect(url_for('admin.manage_users'))
    
    return render_template('admin/edit_user.html', user=user)

@bp.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    if not is_admin():
        flash('无权访问', 'danger')
        return redirect(url_for('main.index'))
    
    if user_id == current_user.id:
        flash('不能删除自己', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    flash('用户已删除', 'success')
    return redirect(url_for('admin.manage_users'))

@bp.route('/admin/courses')
@login_required
def manage_courses():
    if not is_admin():
        flash('无权访问', 'danger')
        return redirect(url_for('main.index'))
    
    courses = Course.query.order_by(Course.category, Course.name).all()
    return render_template('admin/courses.html', courses=courses)

@bp.route('/admin/courses/add', methods=['GET', 'POST'])
@login_required
def add_course():
    if not is_admin():
        flash('无权访问', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        
        if Course.query.filter_by(name=name).first():
            flash('课程已存在', 'danger')
            return redirect(url_for('admin.add_course'))
        
        course = Course(name=name, category=category)
        db.session.add(course)
        db.session.commit()
        
        flash('课程已添加', 'success')
        return redirect(url_for('admin.manage_courses'))
    
    return render_template('admin/add_course.html')

@bp.route('/admin/courses/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    if not is_admin():
        flash('无权访问', 'danger')
        return redirect(url_for('main.index'))
    
    course = Course.query.get_or_404(course_id)
    
    if request.method == 'POST':
        course.name = request.form['name']
        course.category = request.form['category']
        
        db.session.commit()
        flash('课程信息已更新', 'success')
        return redirect(url_for('admin.manage_courses'))
    
    return render_template('admin/edit_course.html', course=course)

@bp.route('/admin/courses/<int:course_id>/delete', methods=['POST'])
@login_required
def delete_course(course_id):
    if not is_admin():
        flash('无权访问', 'danger')
        return redirect(url_for('main.index'))
    
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    
    flash('课程已删除', 'success')
    return redirect(url_for('admin.manage_courses'))

@bp.route('/admin/materials')
@login_required
def manage_materials():
    if not is_admin():
        flash('无权访问', 'danger')
        return redirect(url_for('main.index'))
    
    materials = Material.query.order_by(Material.upload_time.desc()).all()
    return render_template('admin/materials.html', materials=materials)

@bp.route('/admin/materials/<int:material_id>/approve', methods=['POST'])
@login_required
def approve_material(material_id):
    if not is_admin():
        flash('无权访问', 'danger')
        return redirect(url_for('main.index'))
    
    material = Material.query.get_or_404(material_id)
    material.is_approved = True
    db.session.commit()
    
    flash('资料已审核通过', 'success')
    return redirect(url_for('admin.manage_materials'))

@bp.route('/admin/materials/<int:material_id>/delete', methods=['POST'])
@login_required
def delete_material(material_id):
    if not is_admin():
        flash('无权访问', 'danger')
        return redirect(url_for('main.index'))
    
    material = Material.query.get_or_404(material_id)
    
    from app import create_app
    app = create_app()
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], material.file_path)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    db.session.delete(material)
    db.session.commit()
    
    flash('资料已删除', 'success')
    return redirect(url_for('admin.manage_materials'))