import os
import logging
from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_babel import Babel
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

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Create database tables and admin user
with app.app_context():
    # Import models
    import models
    db.create_all()
    
    # Create admin user if not exists
    from models import User
    from werkzeug.security import generate_password_hash
    
    admin = User.query.filter_by(email='heloisasabinobolognesi@gmail.com').first()
    if not admin:
        admin_user = User(
            username='Heloisa',
            email='heloisasabinobolognesi@gmail.com',
            password_hash=generate_password_hash('1234567'),
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
        logging.info("Admin user created")

# Import routes
import routes
