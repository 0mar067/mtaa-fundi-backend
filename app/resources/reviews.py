from flask import request
from flask_restful import Resource
from sqlalchemy import desc
from app.models import Review, User, Job, db
from app.schemas import ReviewCreate, ReviewUpdate, ReviewResponse

class ReviewListResource(Resource):
    """Resource for listing and creating reviews"""

    def get(self):
        """Get reviews by user ID"""
        try:
            user_id = request.args.get('user_id')
            if not user_id:
                return {
                    'success': False,
                    'message': 'user_id parameter is required'
                }, 400

            user = User.query.get_or_404(user_id)

            # Get reviews received by this user
            reviews = Review.query.filter_by(reviewee_id=user_id).order_by(desc(Review.created_at)).all()
            schema = ReviewResponse
            return {
                'success': True,
                'data': [schema.model_validate(review) for review in reviews],
                'count': len(reviews)
            }, 200
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving reviews: {str(e)}'
            }, 500

    def post(self):
        """Create a new review"""
        try:
            schema = ReviewCreate(**request.get_json())

            # Verify that both users exist
            reviewer = User.query.get(schema.reviewer_id)
            reviewee = User.query.get(schema.reviewee_id)

            if not reviewer:
                return {
                    'success': False,
                    'message': 'Reviewer not found'
                }, 404

            if not reviewee:
                return {
                    'success': False,
                    'message': 'Reviewee not found'
                }, 404

            # Verify that the job exists and is completed
            job = Job.query.get(schema.job_id)
            if not job:
                return {
                    'success': False,
                    'message': 'Job not found'
                }, 404

            if job.status != 'closed':
                return {
                    'success': False,
                    'message': 'Can only review completed (closed) jobs'
                }, 403

            # Check if review already exists for this job
            existing_review = Review.query.filter_by(
                reviewer_id=schema.reviewer_id,
                reviewee_id=schema.reviewee_id,
                job_id=schema.job_id
            ).first()

            if existing_review:
                return {
                    'success': False,
                    'message': 'Review already exists for this job'
                }, 409

            # Validate that reviewer and reviewee have different roles
            if reviewer.role == reviewee.role:
                return {
                    'success': False,
                    'message': 'Reviewer and reviewee must have different roles'
                }, 403

            review = Review(
                reviewer_id=schema.reviewer_id,
                reviewee_id=schema.reviewee_id,
                rating=schema.rating,
                comment=schema.comment,
                job_id=schema.job_id
            )
            db.session.add(review)
            db.session.commit()

            response_schema = ReviewResponse.model_validate(review)
            return {
                'success': True,
                'message': 'Review submitted successfully',
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
                'message': f'Error creating review: {str(e)}'
            }, 500

class ReviewResource(Resource):
    """Resource for individual review operations"""

    def get(self, review_id):
        """Get a specific review"""
        try:
            review = Review.query.get_or_404(review_id)
            schema = ReviewResponse.model_validate(review)
            return {
                'success': True,
                'data': schema.model_dump()
            }, 200
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving review: {str(e)}'
            }, 500

    def put(self, review_id):
        """Update a review"""
        try:
            review = Review.query.get_or_404(review_id)
            schema = ReviewUpdate(**request.get_json())

            # Only allow updates to rating and comment
            update_data = schema.model_dump(exclude_unset=True)
            allowed_fields = ['rating', 'comment']
            for key, value in update_data.items():
                if key in allowed_fields and hasattr(review, key):
                    setattr(review, key, value)

            db.session.commit()
            response_schema = ReviewResponse.model_validate(review)
            return {
                'success': True,
                'message': 'Review updated successfully',
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
                'message': f'Error updating review: {str(e)}'
            }, 500

    def delete(self, review_id):
        """Delete a review"""
        try:
            review = Review.query.get_or_404(review_id)
            db.session.delete(review)
            db.session.commit()
            return {
                'success': True,
                'message': 'Review deleted successfully'
            }, 200
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error deleting review: {str(e)}'
            }, 500
