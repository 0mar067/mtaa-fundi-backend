import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

from app import create_app
from app.models import db

app = create_app()

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run()