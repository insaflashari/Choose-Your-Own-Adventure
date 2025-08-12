#job.py
#This file manages story generation jobs — like tracking status of a story creation request.
#Creates a router with prefix /jobs and tag "jobs" for documentation grouping.

import uuid 
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Cookie
from sqlalchemy.orm import Session

from db.database import get_db
from models.job import StoryJob
from schemas.job import StoryJobResponse

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"]
)

#getting job status based on job_id
#Fetches a job by its job_id.
# Returns 404 if not found.
# Returns job info serialized with StoryJobResponse schema.
@router.get("/{job_id}", response_model=StoryJobResponse)
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(StoryJob).filter(StoryJob.job_id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

