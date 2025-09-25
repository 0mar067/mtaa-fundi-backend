from flask import request
from flask_restful import Resource
from sqlalchemy import desc
from app.models import Job, User, db
from app.schemas import JobCreate, JobUpdate, JobResponse

class JobListResource(Resource):
    """Resource for listing and creating jobs"""

def get(self):
    """Get all jobs"""
    try:
        # Get query parameters for filtering
        status = request.args.get('status')
        category = request.args.get('category')
        user_id = request.args.get('user_id')

        query = Job.query

        if status:
            query = query.filter_by(status=status)
        if category:
            query = query.filter_by(category=category)
        if user_id:
            query = query.filter_by(user_id=user_id)

        # Order by creation date (newest first)
        jobs = query.order_by(desc(Job.created_at)).all()

        schema = JobResponse
        return {
            'success': True,
            'data': [schema.model_validate(job) for job in jobs],
            'count': len(jobs)
        }, 200
    except Exception as e:
        return {
            'success': False,
            'message': f'Error retrieving jobs: {str(e)}'
        }, 500

def post(self):
    """Create a new job"""
    try:
        schema = JobCreate(**request.get_json())

        # Verify that the user exists
        user = User.query.get(schema.user_id)
        if not user:
            return {
                'success': False,
                'message': 'User not found'
            }, 404

        # Only homeowners can post jobs
        if user.role != 'homeowner':
            return {
                'success': False,
                'message': 'Only homeowners can post jobs'
            }, 403

        job = Job(
            user_id=schema.user_id,
            title=schema.title,
            description=schema.description,
            category=schema.category,
            preferred_date=schema.preferred_date,
            budget=schema.budget
        )
        db.session.add(job)
        db.session.commit()

        response_schema = JobResponse.model_validate(job)
        return {
            'success': True,
            'message': 'Job created successfully',
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
            'message': f'Error creating job: {str(e)}'
        }, 500
class JobResource(Resource):
    """Resource for individual job operations"""

def get(self, job_id):
    """Get a specific job"""
    try:
        job = Job.query.get_or_404(job_id)
        schema = JobResponse.model_validate(job)
        return {
            'success': True,
            'data': schema.model_dump()
        }, 200
    except Exception as e:
        return {
            'success': False,
            'message': f'Error retrieving job: {str(e)}'
        }, 500

def put(self, job_id):
    """Update a job"""
    try:
        job = Job.query.get_or_404(job_id)
        schema = JobUpdate(**request.get_json())

        # Update job fields
        update_data = schema.model_dump(exclude_unset=True)#
        for key, value in update_data.items():
            if hasattr(job, key):
                setattr(job, key, value)

        db.session.commit()
        response_schema = JobResponse.model_validate(job)
        return {
            'success': True,
            'message': 'Job updated successfully',
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
            'message': f'Error updating job: {str(e)}'
        }, 500

def patch(self, job_id):
    """Partially update a job"""
    return self.put(job_id)  # Same logic as PUT for partial updates

def delete(self, job_id):
    """Delete a job"""
    try:
        job = Job.query.get_or_404(job_id)

        # Only allow deletion if job has no quotes or reviews
        if job.quotes or job.reviews:
            return {
                'success': False,
                'message': 'Cannot delete job with existing quotes or reviews'
            }, 409

        db.session.delete(job)
        db.session.commit()
        return {
            'success': True,
            'message': 'Job deleted successfully'
        }, 200
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'message': f'Error deleting job: {str(e)}'
        }, 500