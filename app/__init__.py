from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api
from flask_cors import CORS
from config import config
import json
from datetime import datetime

def create_app(config_name='default'):
    """Application factory function"""
    app = Flask(__name__)

    # Enable CORS
    CORS(app)

    # Load configuration
    app.config.from_object(config[config_name])

    # Initialize extensions
    from app.models import db
    db.init_app(app)
    migrate = Migrate(app, db)

    # Initialize Flask-RESTful API
    api = Api(app, prefix='/api/v1')

    # Configure custom JSON encoder for datetime serialization
    class CustomJSONEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            # Handle Pydantic models
            if hasattr(obj, 'dict') and callable(getattr(obj, 'dict')):
                return obj.dict()
            # Handle Pydantic models with model_dump (newer versions)
            if hasattr(obj, 'model_dump') and callable(getattr(obj, 'model_dump')):
                return obj.model_dump()
            return super().default(obj)

    # Override Flask-RESTful's JSON representation
    from flask import make_response
    api.representations['application/json'] = lambda data, code, headers=None: make_response(
        json.dumps(data, cls=CustomJSONEncoder, indent=4) + '\n',
        code,
        {**(headers or {}), 'Content-Type': 'application/json'}
    )

    # Import models to ensure they are registered with SQLAlchemy
    from app import models
    
    # Import and register resources
    from app.resources.users import UserListResource, UserResource
    from app.resources.jobs import JobListResource, JobResource
    from app.resources.quotes import QuoteListResource, QuoteResource
    from app.resources.reviews import ReviewListResource, ReviewResource

    # Register API endpoints
    api.add_resource(UserListResource, '/users')
    api.add_resource(UserResource, '/users/<int:user_id>')
    api.add_resource(JobListResource, '/jobs')
    api.add_resource(JobResource, '/jobs/<int:job_id>')
    api.add_resource(QuoteListResource, '/quotes')
    api.add_resource(QuoteResource, '/quotes/<int:quote_id>')
    api.add_resource(ReviewListResource, '/reviews')
    api.add_resource(ReviewResource, '/reviews/<int:review_id>')

    # Add health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        return {
            'status': 'healthy',
            'message': 'Mtaa-Fundi Finder API is running'
        }, 200

    # Add API documentation endpoint
    @app.route('/')
    def api_docs():
        """API documentation endpoint"""
        return {
            'name': 'Mtaa-Fundi Finder API',
            'version': '1.0.0',
            'description': 'API for connecting homeowners with local artisans in Kenya',
            'endpoints': {
                'users': {
                    'GET /api/v1/users': 'List all users',
                    'POST /api/v1/users': 'Create a new user',
                    'GET /api/v1/users/<id>': 'Get user by ID',
                    'PUT /api/v1/users/<id>': 'Update user',
                    'DELETE /api/v1/users/<id>': 'Delete user'
                },
                'jobs': {
                    'GET /api/v1/jobs': 'List all jobs (with optional filters)',
                    'POST /api/v1/jobs': 'Create a new job',
                    'GET /api/v1/jobs/<id>': 'Get job by ID',
                    'PUT /api/v1/jobs/<id>': 'Update job',
                    'DELETE /api/v1/jobs/<id>': 'Delete job'
                },
                'quotes': {
                    'GET /api/v1/quotes?job_id=<id>': 'Get quotes for a job',
                    'POST /api/v1/quotes': 'Create a new quote',
                    'GET /api/v1/quotes/<id>': 'Get quote by ID',
                    'PUT /api/v1/quotes/<id>': 'Update quote',
                    'DELETE /api/v1/quotes/<id>': 'Delete quote'
                },
                'reviews': {
                    'GET /api/v1/reviews?user_id=<id>': 'Get reviews for a user',
                    'POST /api/v1/reviews': 'Create a new review',
                    'GET /api/v1/reviews/<id>': 'Get review by ID',
                    'PUT /api/v1/reviews/<id>': 'Update review',
                    'DELETE /api/v1/reviews/<id>': 'Delete review'
                }
            }
        }, 200

    return app
