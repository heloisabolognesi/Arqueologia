import os
import logging
from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_babel import Babel, gettext, ngettext
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "laari-archaeological-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///laari.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Configure upload settings
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'

# Initialize Babel
babel = Babel()
babel.init_app(app)

# Supported languages
LANGUAGES = {
    'pt': 'Português',
    'en': 'English', 
    'es': 'Español'
}

def get_locale():
    # 1. If user has selected a language, use it
    if 'language' in session:
        return session['language']
    # 2. Otherwise try to guess from browser
    return request.accept_languages.best_match(LANGUAGES.keys()) or 'pt'

babel.locale_selector_func = get_locale

# Configure Babel
app.config['LANGUAGES'] = LANGUAGES
app.config['BABEL_DEFAULT_LOCALE'] = 'pt'
app.config['BABEL_DEFAULT_TIMEZONE'] = 'UTC'

# Simple translation function for demo (replacing full Babel)
def simple_translate(text, lang=None):
    if not lang:
        lang = session.get('language', 'pt')
    
    # Simple translations dictionary
    translations = {
        'en': {
            'Bem-vindo': 'Welcome',
            'Laboratório e Acervo Arqueológico Remoto Integrado': 'Remote Integrated Archaeological Laboratory and Collection',
            'Sistema completo de gestão arqueológica para centralizar documentação, catalogação, acervo e inventário, facilitando a comunicação entre equipes de campo e laboratório.': 'Complete archaeological management system to centralize documentation, cataloging, collection and inventory, facilitating communication between field and laboratory teams.',
            'Entrar': 'Login',
            'Acesse sua conta existente no sistema L.A.A.R.I': 'Access your existing L.A.A.R.I system account',
            'Fazer Login': 'Sign In',
            'Cadastrar': 'Register',
            'Crie uma nova conta para acessar o sistema': 'Create a new account to access the system',
            'Criar Conta': 'Create Account',
            'Funcionalidades Principais': 'Main Features',
            'Acervo Digital': 'Digital Collection',
            'Consulta organizada de todos os itens catalogados': 'Organized consultation of all cataloged items',
            'Catalogação': 'Cataloging',
            'Sistema completo de registro de artefatos': 'Complete artifact registration system',
            'Scanner 3D': '3D Scanner',
            'Integração com digitalização 3D': 'Integration with 3D digitization',
            'Profissionais': 'Professionals',
            'Diretório de arqueólogos da região': 'Directory of archaeologists in the region',
            'Inventário': 'Inventory',
            'Controle completo do inventário': 'Complete inventory control',
            'Transporte': 'Transport',
            'Rastreamento de movimentação': 'Movement tracking'
        },
        'es': {
            'Bem-vindo': 'Bienvenido',
            'Laboratório e Acervo Arqueológico Remoto Integrado': 'Laboratorio y Acervo Arqueológico Remoto Integrado',
            'Sistema completo de gestão arqueológica para centralizar documentação, catalogação, acervo e inventário, facilitando a comunicação entre equipes de campo e laboratório.': 'Sistema completo de gestión arqueológica para centralizar documentación, catalogación, acervo e inventario, facilitando la comunicación entre equipos de campo y laboratorio.',
            'Entrar': 'Ingresar',
            'Acesse sua conta existente no sistema L.A.A.R.I': 'Accede a tu cuenta existente en el sistema L.A.A.R.I',
            'Fazer Login': 'Iniciar Sesión',
            'Cadastrar': 'Registrarse',
            'Crie uma nova conta para acessar o sistema': 'Crea una nueva cuenta para acceder al sistema',
            'Criar Conta': 'Crear Cuenta',
            'Funcionalidades Principais': 'Funcionalidades Principales',
            'Acervo Digital': 'Acervo Digital',
            'Consulta organizada de todos os itens catalogados': 'Consulta organizada de todos los artículos catalogados',
            'Catalogação': 'Catalogación',
            'Sistema completo de registro de artefatos': 'Sistema completo de registro de artefactos',
            'Scanner 3D': 'Escáner 3D',
            'Integração com digitalização 3D': 'Integración con digitalización 3D',
            'Profissionais': 'Profesionales',
            'Diretório de arqueólogos da região': 'Directorio de arqueólogos de la región',
            'Inventário': 'Inventario',
            'Controle completo do inventário': 'Control completo del inventario',
            'Transporte': 'Transporte',
            'Rastreamento de movimentação': 'Seguimiento de movimiento'
        }
    }
    
    if lang in translations and text in translations[lang]:
        return translations[lang][text]
    return text

# Template context processor to make gettext available in templates
@app.context_processor
def inject_conf_vars():
    return {
        'LANGUAGES': LANGUAGES,
        'CURRENT_LANGUAGE': session.get('language', request.accept_languages.best_match(LANGUAGES.keys()) or 'pt'),
        '_': simple_translate,
        'ngettext': ngettext
    }

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Create database tables and admin user
with app.app_context():
    # Import models
    import models
    db.create_all()
    
    # Create admin user if configured via environment variables
    from models import User
    from werkzeug.security import generate_password_hash
    
    admin_email = os.environ.get('ADMIN_EMAIL')
    admin_password = os.environ.get('ADMIN_PASSWORD')
    
    if admin_email and admin_password:
        admin = User.query.filter_by(email=admin_email).first()
        if not admin:
            admin_user = User(
                username=os.environ.get('ADMIN_USERNAME', 'Admin'),
                email=admin_email,
                password_hash=generate_password_hash(admin_password),
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()
            logging.info("Admin user created from environment variables")

# Import routes
import routes
