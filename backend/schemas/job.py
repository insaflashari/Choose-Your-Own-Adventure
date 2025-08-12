#job.py
#This file defines schemas related to the story generation jobs — what 
# data is expected when creating a job and what is returned in responses.
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

#Basic model with just the theme string. Used as a base for creation.
class StoryJobBase(BaseModel):
    theme: str

#The response model sent back to clients when they request job info.

# Includes:
    # job_id — unique job identifier.
    # status — pending, processing, completed, or failed.
    # created_at and optional completed_at timestamps.
    # Optional story_id if story was created.
    # Optional error string in case of failure.
    # from_attributes = True tells Pydantic it can read data from ORM model attributes (SQLAlchemy objects).
class StoryJobResponse(BaseModel):
    job_id: str
    status: str
    created_at: datetime
    story_id: Optional[int] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None

    class Config:
        from_attributes = True

#Inherits from StoryJobBase.
#Used to validate incoming requests when creating a new job.
#No extra fields added here.
class StoryJobCreate(StoryJobBase):
    pass

