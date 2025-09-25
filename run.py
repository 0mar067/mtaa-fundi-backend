#!/usr/bin/env python3
"""
Mtaa-Fundi Finder API
A Flask REST API for connecting homeowners with local artisans in Kenya.

Usage:
    python run.py                    # Run in development mode
    FLASK_ENV=production python run.py  # Run in production mode
"""

from app import create_app
from app.models import db
import os

# Create Flask application
app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()

    # Run the application
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=app.config['DEBUG']
    )
