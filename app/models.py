from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship

db = SQLAlchemy()

# Association table for many-to-many relationship between users and saved jobs
saved_jobs = Table('saved_jobs', db.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('job_id', Integer, ForeignKey('jobs.id'), primary_key=True)
)




class User(db.Model):
    """User model representing both homeowners and fundis (artisans)"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    role = Column(Enum('homeowner', 'fundi', name='user_roles'), nullable=False)
    location = Column(String(100), nullable=False)  # Location in Kenya (e.g., "Nairobi", "Kibera")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    jobs = relationship('Job', back_populates='user', cascade='all, delete-orphan')
    quotes = relationship('Quote', back_populates='fundi', cascade='all, delete-orphan')
    reviews_given = relationship('Review', foreign_keys='Review.reviewer_id', back_populates='reviewer', cascade='all, delete-orphan')
    reviews_received = relationship('Review', foreign_keys='Review.reviewee_id', back_populates='reviewee', cascade='all, delete-orphan')
    saved_jobs = relationship('Job', secondary=saved_jobs, back_populates='saved_by_users')

    def __repr__(self):
        return f'<User {self.name} ({self.role})>'

class Job(db.Model):
    """Job model representing work requests"""
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)  # e.g., "plumbing", "electrical", "painting"
    preferred_date = Column(DateTime, nullable=False)
    budget = Column(Float, nullable=False)
    status = Column(Enum('open', 'closed', name='job_status'), default='open')
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship('User', back_populates='jobs')
    quotes = relationship('Quote', back_populates='job', cascade='all, delete-orphan')
    reviews = relationship('Review', back_populates='job', cascade='all, delete-orphan')
    saved_by_users = relationship('User', secondary=saved_jobs, back_populates='saved_jobs')

    def __repr__(self):
        return f'<Job {self.title} - {self.status}>'

class Quote(db.Model):
    """Quote model representing price quotes for jobs"""
    __tablename__ = 'quotes'

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Fundi providing the quote
    price = Column(Float, nullable=False)
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    job = relationship('Job', back_populates='quotes')
    fundi = relationship('User', back_populates='quotes')

    def __repr__(self):
        return f'<Quote {self.price} KES for Job {self.job_id}>'

class Review(db.Model):
    """Review model for rating users"""
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True)
    reviewer_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # User giving the review
    reviewee_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # User being reviewed
    rating = Column(Integer, nullable=False)  # 1-5 stars
    comment = Column(Text)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    reviewer = relationship('User', foreign_keys=[reviewer_id], back_populates='reviews_given')
    reviewee = relationship('User', foreign_keys=[reviewee_id], back_populates='reviews_received')
    job = relationship('Job', back_populates='reviews')

    def __repr__(self):
        return f'<Review {self.rating}/5 from User {self.reviewer_id} to User {self.reviewee_id}>'

