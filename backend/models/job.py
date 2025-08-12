#job.py

#This table tracks the intent to generate a story. It’s like a job queue:
#job is going to represent intent to make a story

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func #functions

from db.database import Base

class StoryJob(Base):
    __tablename__ = "story_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, index=True, unique=True)
    session_id = Column(String, index=True)
    theme = Column(String)
    status = Column(String)
    story_id = Column(String, nullable=True)
    error = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

#You enqueue a job here when someone wants a new story generated.
#You can track if the job is done and the generated story’s ID.
#Stores metadata about the job, like creation and completion time.
