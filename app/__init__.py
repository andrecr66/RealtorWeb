from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from datetime import datetime # Import datetime
from app.models.models import Testimonial # Import Testimonial model

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin.login' # Route for login page (admin blueprint, login view)
login_manager.login_message_category = 'info' # Category for the "Please log in" message
login_manager.session_protection = "strong" # Protect against session tampering

# User loader function - must be defined here or imported AFTER login_manager is defined
@login_manager.user_loader
def load_user(user_id):
    from app.models.models import AdminUser
    return AdminUser.query.get(int(user_id))

# Context processor to inject variables into all templates
@app.context_processor
def inject_global_vars():
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
from app.routes import main_routes
app.register_blueprint(main_routes.bp)

from app.routes.admin_routes import admin_bp # Import admin_bp
app.register_blueprint(admin_bp) # Register admin_bp

if __name__ == '__main__':
    app.run(debug=True)
