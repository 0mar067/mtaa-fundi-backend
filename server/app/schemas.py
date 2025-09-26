from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator
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
        orm_mode = True
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
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class QuoteResponse(QuoteBase):
    id: int
    created_at: datetime
    job: Optional[JobResponse] = None
    fundi: Optional[UserResponse] = None

    class Config:
        orm_mode = True
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
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }