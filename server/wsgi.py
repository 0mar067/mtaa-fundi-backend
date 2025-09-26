import os
from app import create_app
from app.models import db

# Create Flask application
application = create_app(os.getenv('FLASK_ENV', 'development'))

# Create database tables if they don't exist
with application.app_context():
    db.create_all()

if __name__ == "__main__":
    application.run()