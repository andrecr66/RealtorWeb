# run.py

from app import create_app, db # Import db if you need to use it here, e.g. for shell context
from app.models.models import AdminUser, Agent, Property # Import models to make them known for shell context etc.

app = create_app()

# Optional: Add models to Flask shell context for easier debugging
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'AdminUser': AdminUser, 'Agent': Agent, 'Property': Property}

if __name__ == '__main__':
    app.run(debug=True) # Set debug=False for production