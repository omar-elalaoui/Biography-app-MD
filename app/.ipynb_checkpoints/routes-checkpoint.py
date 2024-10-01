from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
import os
from app import db
from app.models import User, Bibliography

bp = Blueprint('routes', __name__)

def save_picture(form_picture):
    picture_fn = secure_filename(form_picture.filename)
    picture_path = os.path.join(current_app.root_path, 'static/images', picture_fn)
    form_picture.save(picture_path)
    return picture_fn

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes.dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash('Invalid username or password')
            return redirect(url_for('routes.login'))
        login_user(user)
        return redirect(url_for('routes.dashboard'))
    return render_template('login.html')

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('routes.login'))

@bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        if 'image_file' in request.files:
            image_file = save_picture(request.files['image_file'])
            current_user.image_file = image_file
            db.session.commit()
            flash('Your image has been updated!')
    bibliographies = current_user.bibliographies.all()
    return render_template('dashboard.html', bibliographies=bibliographies, image_file=current_user.image_file)

@bp.route('/bibliography/new', methods=['GET', 'POST'])
@login_required
def new_bibliography():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        biblio = Bibliography(title=title, content=content, author=current_user)
        db.session.add(biblio)
        db.session.commit()
        flash('Your bibliography has been created!')
        return redirect(url_for('routes.dashboard'))
    return render_template('edit_bibliography.html')

@bp.route('/bibliography/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_bibliography(id):
    biblio = Bibliography.query.get_or_404(id)
    if biblio.author != current_user:
        return redirect(url_for('routes.dashboard'))
    if request.method == 'POST':
        biblio.title = request.form['title']
        biblio.content = request.form['content']
        db.session.commit()
        flash('Your bibliography has been updated!')
        return redirect(url_for('routes.dashboard'))
    return render_template('edit_bibliography.html', biblio=biblio)

@bp.route('/bibliography/<int:id>/delete', methods=['POST'])
@login_required
def delete_bibliography(id):
    biblio = Bibliography.query.get_or_404(id)
    if biblio.author != current_user:
        return redirect(url_for('routes.dashboard'))
    db.session.delete(biblio)
    db.session.commit()
    flash('Your bibliography has been deleted!')
    return redirect(url_for('routes.dashboard'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('routes.dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('routes.login'))
    return render_template('register.html')