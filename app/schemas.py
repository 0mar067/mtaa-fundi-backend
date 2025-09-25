from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator, EmailStr
from enum import Enum

class UserRole(str, Enum):
    HOMEOWNER = "homeowner"
    FUNDI = "fundi"

class JobStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"

class JobCategory(str, Enum):
    PLUMBING = "plumbing"
    ELECTRICAL = "electrical"
    PAINTING = "painting"
    CARPENTRY = "carpentry"
    MASONRY = "masonry"
    ROOFING = "roofing"
    GARDENING = "gardening"
    CLEANING = "cleaning"
    SECURITY = "security"
    OTHER = "other"

# Base schemas for requests
class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(...)
    role: UserRole
    location: str = Field(..., min_length=1, max_length=100)

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = None
    role: Optional[UserRole] = None
    location: Optional[str] = Field(None, min_length=1, max_length=100)

class JobBase(BaseModel):
    user_id: int
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    category: JobCategory
    preferred_date: datetime
    budget: float

class JobCreate(JobBase):
    pass

class JobUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[JobCategory] = None
    preferred_date: Optional[datetime] = None
    budget: Optional[float] = None
    status: Optional[JobStatus] = None

class QuoteBase(BaseModel):
    job_id: int
    user_id: int
    price: float
    message: Optional[str] = None

class QuoteCreate(QuoteBase):
    pass

class QuoteUpdate(BaseModel):
    price: Optional[float] = None
    message: Optional[str] = None

class ReviewBase(BaseModel):
    reviewer_id: int
    reviewee_id: int
    rating: int
    comment: Optional[str] = None
    job_id: int

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(BaseModel):
    rating: Optional[int] = None
    comment: Optional[str] = None

# Response schemas with relationships
class UserResponse(UserBase):
    id: int
    created_at: datetime
    jobs_count: Optional[int] = 0
    quotes_count: Optional[int] = 0
    average_rating: Optional[float] = 0.0

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class JobResponse(JobBase):
    id: int
    status: JobStatus
    created_at: datetime
    user: Optional[UserResponse] = None
    quotes_count: Optional[int] = 0

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class QuoteResponse(QuoteBase):
    id: int
    created_at: datetime
    job: Optional[JobResponse] = None
    fundi: Optional[UserResponse] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ReviewResponse(ReviewBase):
    id: int
    created_at: datetime
    reviewer: Optional[UserResponse] = None
    reviewee: Optional[UserResponse] = None
    job: Optional[JobResponse] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Validation functions
def validate_phone(phone: str) -> str:
    """Validate Kenyan phone number format"""
    if not phone.startswith('+254') and not phone.startswith('254') and not phone.startswith('0'):
        raise ValueError('Phone number must be in Kenyan format (e.g., +2547XX XXX XXX or 07XX XXX XXX)')

    # Basic length validation
    clean_phone = phone.replace('+254', '').replace('254', '').replace('0', '')
    if len(clean_phone) != 9:
        raise ValueError('Phone number must have 9 digits after country/area code')

    return phone

def validate_budget(budget: float) -> float:
    """Validate budget range"""
    if budget < 100:
        raise ValueError('Budget must be at least 100 KES')
    if budget > 50000:
        raise ValueError('Budget cannot exceed 50,000 KES')
    return budget

def validate_rating(rating: int) -> int:
    """Validate rating range"""
    if not isinstance(rating, int) or rating < 1 or rating > 5:
        raise ValueError('Rating must be an integer between 1 and 5')
    return rating

def validate_price(price: float) -> float:
    """Validate quote price"""
    if price <= 0:
        raise ValueError('Price must be greater than 0')
    if price > 100000:
        raise ValueError('Price cannot exceed 100,000 KES')
    return price

def validate_preferred_date(preferred_date: datetime) -> datetime:
    """Validate that preferred date is not in the past"""
    if preferred_date < datetime.utcnow():
        raise ValueError('Preferred date cannot be in the past')
    return preferred_date

# Custom validators for Pydantic models
@validator('phone')
def validate_user_phone(cls, v):
    return validate_phone(v)

@validator('budget')
def validate_job_budget(cls, v):
    return validate_budget(v)

@validator('preferred_date')
def validate_job_date(cls, v):
    return validate_preferred_date(v)

@validator('category')
def validate_job_category(cls, v):
    return v.lower()

@validator('price')
def validate_quote_price(cls, v):
    return validate_price(v)

@validator('rating')
def validate_review_rating(cls, v):
    return validate_rating(v)
