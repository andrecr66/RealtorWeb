# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from datetime import datetime

# Create extension instances WITHOUT an app yet
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'admin.login' # Route for login page (admin blueprint, login view)
login_manager.login_message_category = 'info' # Category for the "Please log in" message
login_manager.session_protection = "strong" # Protect against session tampering

# Moved AdminUser import here as it's only used by load_user which is tied to login_manager
# Alternatively, import it inside load_user, but this is fine too.
from app.models.models import AdminUser, Testimonial # Keep Testimonial if used in context_processor directly

# User loader function
@login_manager.user_loader
def load_user(user_id):
    # from app.models.models import AdminUser # Or import here if preferred
    return AdminUser.query.get(int(user_id))

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db) # Pass db here
    login_manager.init_app(app)

    # Context processor to inject variables into all templates
    @app.context_processor
    def inject_global_vars():
        # This import is fine here because create_app is called, and Testimonial is already imported above
        # or you could move 'from app.models.models import Testimonial' inside this function
        def get_testimonials_for_about_page(limit=3):
            return Testimonial.query.order_by(Testimonial.date.desc()).limit(limit).all()

        return {
            'JINJA_GLOBALS': {
                'current_year': datetime.utcnow().year
            },
            'isinstance': isinstance, # Make isinstance available in templates
            'AdminUser': AdminUser, # Make AdminUser class available for type checking
            'get_testimonials_for_about_page': get_testimonials_for_about_page
        }

    # Import and register blueprints
    # It's crucial that blueprints are imported AFTER app and extensions are initialized
    # And that the blueprint files correctly import 'db' or models
    from app.routes import main_routes
    app.register_blueprint(main_routes.bp)

    from app.routes.admin_routes import admin_bp
    app.register_blueprint(admin_bp)
    
    # This ensures models are known to SQLAlchemy and Flask-Migrate
    # by the time the app is fully created and returned.
    # The imports within your models files (app/models/models.py) should correctly get 'db'.
    from app import models # This will trigger app/models/__init__.py

    return app

# The following is for when you run 'python app/__init__.py' directly, which is not typical for Flask apps.
# Usually, 'run.py' is the entry point.
# if __name__ == '__main__':
#     # This creates a circular dependency if run.py also creates an app
#     # It's better to handle app running in run.py
#     # app_instance = create_app()
#     # app_instance.run(debug=True)
#     pass