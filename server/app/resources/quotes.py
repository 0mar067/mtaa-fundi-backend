from flask import request
from flask_restful import Resource
from sqlalchemy import desc
from app.models import Quote, Job, User, db
from app.schemas import QuoteCreate, QuoteUpdate, QuoteResponse

class QuoteListResource(Resource):
    """Resource for listing and creating quotes"""

    def get(self):
        """Get quotes by job ID"""
        try:
            job_id = request.args.get('job_id')
            if not job_id:
                return {
                    'success': False,
                    'message': 'job_id parameter is required'
                }, 400

            job = Job.query.get_or_404(job_id)

            # Only allow quotes to be viewed if job is open
            if job.status != 'open':
                return {
                    'success': False,
                    'message': 'Cannot view quotes for closed jobs'
                }, 403

            quotes = Quote.query.filter_by(job_id=job_id).order_by(desc(Quote.created_at)).all()
            schema = QuoteResponse
            return {
                'success': True,
                'data': [schema.model_validate(quote) for quote in quotes],
                'count': len(quotes)
            }, 200
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving quotes: {str(e)}'
            }, 500

    def post(self):
        """Create a new quote"""
        try:
            schema = QuoteCreate(**request.get_json())

            # Verify that the job exists and is open
            job = Job.query.get(schema.job_id)
            if not job:
                return {
                    'success': False,
                    'message': 'Job not found'
                }, 404

            if job.status != 'open':
                return {
                    'success': False,
                    'message': 'Cannot quote on closed jobs'
                }, 403

            # Verify that the user exists and is a fundi
            fundi = User.query.get(schema.user_id)
            if not fundi:
                return {
                    'success': False,
                    'message': 'User not found'
                }, 404

            if fundi.role != 'fundi':
                return {
                    'success': False,
                    'message': 'Only fundis can provide quotes'
                }, 403

            # Check if fundi already quoted on this job
            existing_quote = Quote.query.filter_by(job_id=schema.job_id, user_id=schema.user_id).first()
            if existing_quote:
                return {
                    'success': False,
                    'message': 'You have already quoted on this job'
                }, 409

            quote = Quote(
                job_id=schema.job_id,
                user_id=schema.user_id,
                price=schema.price,
                message=schema.message
            )
            db.session.add(quote)
            db.session.commit()

            response_schema = QuoteResponse.model_validate(quote)
            return {
                'success': True,
                'message': 'Quote submitted successfully',
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
                'message': f'Error creating quote: {str(e)}'
            }, 500

class QuoteResource(Resource):
    """Resource for individual quote operations"""

    def get(self, quote_id):
        """Get a specific quote"""
        try:
            quote = Quote.query.get_or_404(quote_id)
            schema = QuoteResponse.model_validate(quote)
            return {
                'success': True,
                'data': schema.model_dump()
            }, 200
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving quote: {str(e)}'
            }, 500

    def put(self, quote_id):
        """Update a quote"""
        try:
            quote = Quote.query.get_or_404(quote_id)
            schema = QuoteUpdate(**request.get_json())

            # Only allow updates to price and message
            update_data = schema.model_dump(exclude_unset=True)
            allowed_fields = ['price', 'message']
            for key, value in update_data.items():
                if key in allowed_fields and hasattr(quote, key):
                    setattr(quote, key, value)

            db.session.commit()
            response_schema = QuoteResponse.model_validate(quote)
            return {
                'success': True,
                'message': 'Quote updated successfully',
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
                'message': f'Error updating quote: {str(e)}'
            }, 500

    def delete(self, quote_id):
        """Delete a quote"""
        try:
            quote = Quote.query.get_or_404(quote_id)
            db.session.delete(quote)
            db.session.commit()
            return {
                'success': True,
                'message': 'Quote deleted successfully'
            }, 200
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error deleting quote: {str(e)}'
            }, 500
