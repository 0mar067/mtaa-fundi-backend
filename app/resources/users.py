from flask import request
from flask_restful import Resource
from app.models import User, db
from app.schemas import UserCreate, UserUpdate, UserResponse

class UserListResource(Resource):
    """Resource for listing and creating users"""

    def get(self):
        """Get all users"""
        try:
            users = User.query.all()
            schema = UserResponse
            return {
                'success': True,
                'data': [schema.model_validate(user) for user in users],
                'count': len(users)
            }, 200
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving users: {str(e)}'
            }, 500

    def post(self):
        """Create a new user"""
        try:
            schema = UserCreate(**request.get_json())

            # Check if phone number already exists
            existing_user = User.query.filter_by(phone=schema.phone).first()
            if existing_user:
                return {
                    'success': False,
                    'message': 'Phone number already registered'
                }, 409

            user = User(
                name=schema.name,
                phone=schema.phone,
                role=schema.role,
                location=schema.location
            )
            db.session.add(user)
            db.session.commit()

            response_schema = UserResponse.model_validate(user)
            return {
                'success': True,
                'message': 'User created successfully',
                'data': response_schema.model_dump()
            }, 201

        except ValueError as e:
            return {
                'success': False,
                'message': 'Validation error',
                'errors': str(e)
            }, 400
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error creating user: {str(e)}'
            }, 500

class UserResource(Resource):
    """Resource for individual user operations"""

    def get(self, user_id):
        """Get a specific user"""
        try:
            user = User.query.get_or_404(user_id)
            schema = UserResponse.model_validate(user)
            return {
                'success': True,
                'data': schema.model_dump()
            }, 200
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving user: {str(e)}'
            }, 500

    def put(self, user_id):
        """Update a user"""
        try:
            user = User.query.get_or_404(user_id)
            schema = UserUpdate(**request.get_json())

            # Check if phone number is being updated and already exists
            if schema.phone and schema.phone != user.phone:
                existing_user = User.query.filter_by(phone=schema.phone).first()
                if existing_user:
                    return {
                        'success': False,
                        'message': 'Phone number already registered'
                    }, 409

            # Update user fields
            update_data = schema.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)

            db.session.commit()
            response_schema = UserResponse.model_validate(user)
            return {
                'success': True,
                'message': 'User updated successfully',
                'data': response_schema.model_dump()
            }, 200

        except ValueError as e:
            return {
                'success': False,
                'message': 'Validation error',
                'errors': str(e)
            }, 400
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error updating user: {str(e)}'
            }, 500

    def delete(self, user_id):
        """Delete a user"""
        try:
            user = User.query.get_or_404(user_id)
            db.session.delete(user)
            db.session.commit()
            return {
                'success': True,
                'message': 'User deleted successfully'
            }, 200
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error deleting user: {str(e)}'
            }, 500
