import os
import uuid
from flask import render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime

from app import app, db
from models import User, Artifact, Professional, Transport, Scanner3D
from forms import LoginForm, RegisterForm, ArtifactForm, ProfessionalForm, TransportForm, Scanner3DForm, AdminUserForm

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_uploaded_file(file, folder='uploads'):
    if file and file.filename:
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(folder, unique_filename)
        os.makedirs(folder, exist_ok=True)
        file.save(file_path)
        return file_path
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            if user.is_active_user:
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                flash('Sua conta está desativada. Contate o administrador.', 'error')
        else:
            flash('Email ou senha incorretos.', 'error')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Este email já está cadastrado.', 'error')
        else:
            user = User(
                username=form.username.data,
                email=form.email.data,
                password_hash=generate_password_hash(form.password.data)
            )
            db.session.add(user)
            db.session.commit()
            flash('Cadastro realizado com sucesso! Faça login.', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get some statistics
    total_artifacts = Artifact.query.count()
    total_professionals = Professional.query.count()
    pending_transports = Transport.query.filter_by(status='pendente').count()
    
    stats = {
        'artifacts': total_artifacts,
        'professionals': total_professionals,
        'pending_transports': pending_transports
    }
    
    return render_template('dashboard.html', stats=stats)

@app.route('/catalogacao')
@login_required
def catalogacao():
    artifacts = Artifact.query.order_by(Artifact.created_at.desc()).all()
    return render_template('catalogacao.html', artifacts=artifacts)

@app.route('/catalogar_novo', methods=['GET', 'POST'])
@login_required
def catalogar_novo():
    form = ArtifactForm()
    if form.validate_on_submit():
        artifact = Artifact(
            name=form.name.data,
            discovery_date=form.discovery_date.data,
            origin_location=form.origin_location.data,
            artifact_type=form.artifact_type.data,
            conservation_state=form.conservation_state.data,
            observations=form.observations.data,
            user_id=current_user.id,
            qr_code=f"LAARI-{uuid.uuid4().hex[:8].upper()}"
        )
        
        # Handle photo upload
        if form.photo.data:
            photo_path = save_uploaded_file(form.photo.data, 'uploads/photos')
            artifact.photo_path = photo_path
        
        # Handle 3D model upload
        if form.model_3d.data:
            model_path = save_uploaded_file(form.model_3d.data, 'uploads/3d_models')
            artifact.model_3d_path = model_path
        
        db.session.add(artifact)
        db.session.commit()
        flash('Artefato catalogado com sucesso!', 'success')
        return redirect(url_for('catalogacao'))
    
    return render_template('catalogar_novo.html', form=form)

@app.route('/acervo')
@login_required
def acervo():
    artifacts = Artifact.query.order_by(Artifact.name).all()
    return render_template('acervo.html', artifacts=artifacts)

@app.route('/inventario')
@login_required
def inventario():
    artifacts = Artifact.query.order_by(Artifact.created_at.desc()).all()
    return render_template('inventario.html', artifacts=artifacts)

@app.route('/profissionais')
@login_required
def profissionais():
    professionals = Professional.query.order_by(Professional.name).all()
    return render_template('profissionais.html', professionals=professionals)

@app.route('/profissional/<int:id>')
@login_required
def perfil_profissional(id):
    professional = Professional.query.get_or_404(id)
    return render_template('perfil_profissional.html', professional=professional)

@app.route('/adicionar_profissional', methods=['GET', 'POST'])
@login_required
def adicionar_profissional():
    form = ProfessionalForm()
    if form.validate_on_submit():
        professional = Professional(
            name=form.name.data,
            age=form.age.data,
            specialization=form.specialization.data,
            description=form.description.data,
            experience=form.experience.data
        )
        
        # Handle profile photo upload
        if form.profile_photo.data:
            photo_path = save_uploaded_file(form.profile_photo.data, 'uploads/profiles')
            professional.profile_photo = photo_path
        
        db.session.add(professional)
        db.session.commit()
        flash('Profissional adicionado com sucesso!', 'success')
        return redirect(url_for('profissionais'))
    
    return render_template('adicionar_profissional.html', form=form)

@app.route('/scanner_3d', methods=['GET', 'POST'])
@login_required
def scanner_3d():
    form = Scanner3DForm()
    
    # Populate artifact choices
    artifacts = Artifact.query.all()
    form.artifact_id.choices = [(a.id, f"{a.name} - {a.qr_code}") for a in artifacts]
    
    if form.validate_on_submit():
        scan = Scanner3D(
            artifact_id=form.artifact_id.data,
            scanner_type=form.scanner_type.data,
            resolution=form.resolution.data,
            notes=form.notes.data
        )
        
        # Handle scan file upload
        if form.scan_file.data:
            file_path = save_uploaded_file(form.scan_file.data, 'uploads/3d_scans')
            scan.file_path = file_path
            # Get file size
            if os.path.exists(file_path):
                scan.file_size = os.path.getsize(file_path)
        
        db.session.add(scan)
        db.session.commit()
        flash('Scan 3D registrado com sucesso!', 'success')
        return redirect(url_for('scanner_3d'))
    
    scans = Scanner3D.query.order_by(Scanner3D.scan_date.desc()).all()
    return render_template('scanner_3d.html', form=form, scans=scans)

@app.route('/transporte', methods=['GET', 'POST'])
@login_required
def transporte():
    form = TransportForm()
    
    # Populate artifact choices
    artifacts = Artifact.query.all()
    form.artifact_id.choices = [(a.id, f"{a.name} - {a.qr_code}") for a in artifacts]
    
    if form.validate_on_submit():
        transport = Transport(
            artifact_id=form.artifact_id.data,
            origin_location=form.origin_location.data,
            destination_location=form.destination_location.data,
            transport_date=form.transport_date.data,
            responsible_person=form.responsible_person.data,
            status=form.status.data,
            notes=form.notes.data
        )
        
        db.session.add(transport)
        db.session.commit()
        flash('Transporte registrado com sucesso!', 'success')
        return redirect(url_for('transporte'))
    
    transports = Transport.query.order_by(Transport.created_at.desc()).all()
    return render_template('transporte.html', form=form, transports=transports)

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('Acesso negado. Apenas administradores podem acessar esta página.', 'error')
        return redirect(url_for('dashboard'))
    
    users = User.query.all()
    return render_template('admin.html', users=users)

@app.route('/admin/toggle_user/<int:user_id>')
@login_required
def toggle_user_status(user_id):
    if not current_user.is_admin:
        flash('Acesso negado.', 'error')
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Você não pode desativar sua própria conta.', 'error')
    else:
        user.is_active_user = not user.is_active_user
        db.session.commit()
        status = "ativado" if user.is_active_user else "desativado"
        flash(f'Usuário {user.username} foi {status}.', 'success')
    
    return redirect(url_for('admin'))

@app.route('/admin/toggle_admin/<int:user_id>')
@login_required
def toggle_admin_status(user_id):
    if not current_user.is_admin:
        flash('Acesso negado.', 'error')
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Você não pode remover seus próprios privilégios de administrador.', 'error')
    else:
        user.is_admin = not user.is_admin
        db.session.commit()
        status = "promovido a administrador" if user.is_admin else "removido da administração"
        flash(f'Usuário {user.username} foi {status}.', 'success')
    
    return redirect(url_for('admin'))

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
