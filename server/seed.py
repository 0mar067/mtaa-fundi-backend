#!/usr/bin/env python3
"""
Database seeding script for Mtaa-Fundi Finder API
Seeds the database with sample users, jobs, quotes, and reviews.
"""

from datetime import datetime, timedelta
from app import create_app
from app.models import db, User, Job, Quote, Review

def seed_database():
    """Seed the database with sample data"""

    # Create sample users
    users_data = [
        {
            'name': 'John Mwangi',
            'phone': '+254712345678',
            'role': 'homeowner',
            'location': 'Nairobi, Westlands'
        },
        {
            'name': 'Mary Wanjiku',
            'phone': '+254723456789',
            'role': 'homeowner',
            'location': 'Nairobi, Karen'
        },
        {
            'name': 'Peter Kiprop',
            'phone': '+254734567890',
            'role': 'fundi',
            'location': 'Nairobi, Kibera'
        },
        {
            'name': 'Grace Achieng',
            'phone': '+254745678901',
            'role': 'fundi',
            'location': 'Nairobi, Eastlands'
        },
        {
            'name': 'David Ochieng',
            'phone': '+254756789012',
            'role': 'fundi',
            'location': 'Nairobi, Kawangware'
        }
    ]

    print("Creating users...")
    users = []
    for user_data in users_data:
        user = User(**user_data)
        db.session.add(user)
        users.append(user)

    db.session.commit()
    print(f"Created {len(users)} users")

    # Create sample jobs
    jobs_data = [
        {
            'user_id': 1,  # John Mwangi (homeowner)
            'title': 'Fix leaking kitchen tap',
            'description': 'Kitchen tap has been leaking for a week. Need urgent repair.',
            'category': 'plumbing',
            'preferred_date': datetime.utcnow() + timedelta(days=2),
            'budget': 1500
        },
        {
            'user_id': 1,  # John Mwangi (homeowner)
            'title': 'Install ceiling fan in living room',
            'description': 'Need to install a new ceiling fan. Already have the fan, just need installation.',
            'category': 'electrical',
            'preferred_date': datetime.utcnow() + timedelta(days=5),
            'budget': 2500
        },
        {
            'user_id': 2,  # Mary Wanjiku (homeowner)
            'title': 'Paint bedroom walls',
            'description': 'Need to paint one bedroom. Paint will be provided.',
            'category': 'painting',
            'preferred_date': datetime.utcnow() + timedelta(days=3),
            'budget': 8000
        },
        {
            'user_id': 2,  # Mary Wanjiku (homeowner)
            'title': 'Fix broken door lock',
            'description': 'Front door lock is not working properly. Need replacement.',
            'category': 'carpentry',
            'preferred_date': datetime.utcnow() + timedelta(days=1),
            'budget': 1200
        }
    ]

    print("Creating jobs...")
    jobs = []
    for job_data in jobs_data:
        job = Job(**job_data)
        db.session.add(job)
        jobs.append(job)

    db.session.commit()
    print(f"Created {len(jobs)} jobs")

    # Create sample quotes
    quotes_data = [
        {
            'job_id': 1,  # Fix leaking kitchen tap
            'user_id': 3,  # Peter Kiprop (fundi)
            'price': 1200,
            'message': 'I can fix this today. I have all necessary tools and spare parts.'
        },
        {
            'job_id': 1,  # Fix leaking kitchen tap
            'user_id': 5,  # David Ochieng (fundi)
            'price': 1000,
            'message': 'Available immediately. Will bring all required materials.'
        },
        {
            'job_id': 2,  # Install ceiling fan
            'user_id': 4,  # Grace Achieng (fundi)
            'price': 2000,
            'message': 'Experienced electrician. Can install safely and provide warranty.'
        },
        {
            'job_id': 3,  # Paint bedroom walls
            'user_id': 4,  # Grace Achieng (fundi)
            'price': 7000,
            'message': 'Professional painting service. Will use quality paint and finish in one day.'
        },
        {
            'job_id': 4,  # Fix broken door lock
            'user_id': 3,  # Peter Kiprop (fundi)
            'price': 1000,
            'message': 'Can fix this quickly. Have various lock options available.'
        }
    ]

    print("Creating quotes...")
    quotes = []
    for quote_data in quotes_data:
        quote = Quote(**quote_data)
        db.session.add(quote)
        quotes.append(quote)

    db.session.commit()
    print(f"Created {len(quotes)} quotes")

    # Create sample reviews (after closing some jobs)
    # First, close job 1 and 4
    jobs[0].status = 'closed'  # Fix leaking kitchen tap
    jobs[3].status = 'closed'  # Fix broken door lock

    reviews_data = [
        {
            'reviewer_id': 1,  # John Mwangi (homeowner)
            'reviewee_id': 3,  # Peter Kiprop (fundi)
            'rating': 5,
            'comment': 'Excellent work! Fixed the tap quickly and professionally.',
            'job_id': 1
        },
        {
            'reviewer_id': 1,  # John Mwangi (homeowner)
            'reviewee_id': 5,  # David Ochieng (fundi)
            'rating': 4,
            'comment': 'Good work, arrived on time and completed the job well.',
            'job_id': 1
        },
        {
            'reviewer_id': 2,  # Mary Wanjiku (homeowner)
            'reviewee_id': 3,  # Peter Kiprop (fundi)
            'rating': 5,
            'comment': 'Very skilled carpenter. Fixed the lock perfectly.',
            'job_id': 4
        }
    ]

    print("Creating reviews...")
    reviews = []
    for review_data in reviews_data:
        review = Review(**review_data)
        db.session.add(review)
        reviews.append(review)

    db.session.commit()
    print(f"Created {len(reviews)} reviews")

    print("\n=== Database Seeding Complete ===")
    print(f"Total Users: {len(users)}")
    print(f"Total Jobs: {len(jobs)}")
    print(f"Total Quotes: {len(quotes)}")
    print(f"Total Reviews: {len(reviews)}")

    print("\n=== Sample Data Summary ===")
    print("Users:")
    for user in users:
        print(f"  - {user.name} ({user.role}) - {user.phone}")

    print("\nJobs:")
    for job in jobs:
        print(f"  - {job.title} by {job.user.name} - {job.status}")

    print("\nQuotes:")
    for quote in quotes:
        print(f"  - {quote.price} KES by {quote.fundi.name} for '{quote.job.title}'")

    print("\nReviews:")
    for review in reviews:
        print(f"  - {review.rating}/5 from {review.reviewer.name} to {review.reviewee.name}")

if __name__ == '__main__':
    # Create Flask app context
    app = create_app()

    with app.app_context():
        # Clear existing data (optional - uncomment if needed)
        # db.drop_all()
        # db.create_all()

        # Seed the database
        seed_database()
