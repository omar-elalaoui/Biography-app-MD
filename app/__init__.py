from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate  # Add Flask-Migrate
from config import Config

db = SQLAlchemy()
login = LoginManager()
login.login_view = 'routes.login'
migrate = Migrate()  # Initialize Flask-Migrate

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    login.init_app(app)
    migrate.init_app(app, db)  # Bind Flask-Migrate to the app and db
    
    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)
    
    return app