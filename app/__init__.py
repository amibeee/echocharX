from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
from datetime import datetime


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Register blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.admin_routes import admin_bp
    from app.routes.supplier_routes import supplier_bp
    from app.routes.client_routes import client_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(supplier_bp)
    app.register_blueprint(client_bp)
    
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
        
        # Initialize admin account if not exists
        from app.models import User, Role
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(name='admin')
            db.session.add(admin_role)
            
        supplier_role = Role.query.filter_by(name='supplier').first()
        if not supplier_role:
            supplier_role = Role(name='supplier')
            db.session.add(supplier_role)
            
        client_role = Role.query.filter_by(name='client').first()
        if not client_role:
            client_role = Role(name='client')
            db.session.add(client_role)
            
        db.session.commit()
        
        admin_user = User.query.filter_by(email='admin@echocharx.com').first()
        if not admin_user:
            from werkzeug.security import generate_password_hash
            admin_user = User(
                name='Admin',
                email='admin@echocharx.com',
                password_hash=generate_password_hash('admin123'),
                role_id=admin_role.id
            )
            db.session.add(admin_user)
            db.session.commit()
        @app.context_processor
        def inject_now():
            return {'now': datetime.now()}

    return app