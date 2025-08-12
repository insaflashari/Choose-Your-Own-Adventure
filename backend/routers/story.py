#story.py
#This file handles creating stories and fetching complete stories with all nodes.

import uuid
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Cookie, Response, BackgroundTasks
from sqlalchemy.orm import Session

from db.database import get_db, SessionLocal
from models.story import Story, StoryNode
from models.job import StoryJob
from schemas.story import (
    CompleteStoryResponse, CompleteStoryNodeResponse, CreateStoryRequest
)
from schemas.job import StoryJobResponse
from core.story_generator import StoryGenerator

#organizing the story specific routes
# Router for /stories endpoints.
# Imports models, schemas, and the story generator utility.
router = APIRouter(
    prefix="/stories",
    tags=["stories"]
)

#session will identify your browser when your interacting with a website
#They can expire, they can store info, so website does not have to keep loading new info
#store id of ur browser and re-poplate the state

#creates session_id
# Checks if the client has a cookie named session_id.
# If not, creates a new UUID as the session id.
# Ensures each client has a unique session identifier tracked via cookie.
#HELPER
def get_session_id(session_id: Optional[str] = Cookie(None)):
    if not session_id:
        session_id = str(uuid.uuid4())
    return session_id

#Takes a request with a theme (e.g., "fantasy").
    # Assigns or reuses a session id cookie.
    # Creates a new StoryJob with pending status.
    # Saves the job in DB.
    # Starts generate_story_task in background (async task) to generate the story without blocking the API response.
    # Returns the job info immediately (so frontend can poll job status).
#CREATE A NEW STORY JOB
#endpoints
@router.post("/create", response_model=StoryJobResponse)

#inject these dependencies into these parameters 
def create_story(
        request: CreateStoryRequest,
        background_tasks: BackgroundTasks,
        response: Response,
        session_id: str = Depends(get_session_id),
        db: Session = Depends(get_db)
):
    response.set_cookie(key="session_id", value=session_id, httponly=True)

    #call LLM in openai to create a story (JOB)

    job_id = str(uuid.uuid4())

    #create a new instance of StoryJob
    job = StoryJob(
        job_id = job_id, 
        session_id = session_id,
        theme = request.theme, 
        status = "pending"
    )

    db.add(job) #staging it in database, job of orm
    db.commit() #save into database

    background_tasks.add_task(
        generate_story_task,
        job_id = job_id,
        theme = request.theme, 
        session_id = session_id
    )

    return job

# Opens a fresh DB session (important for background tasks).
# Updates job status to "processing".
# Calls StoryGenerator.generate_story() which:
# Generates the story using GPT.
# Saves story and nodes to DB.
# Updates job status to "completed" and saves story id.
# On error, marks job as "failed" and logs the error.
# Always closes DB session.

#BACKGROUND TASK
def generate_story_task(job_id: str, theme: str, session_id: str):
    db = SessionLocal()

    try:
        job = db.query(StoryJob).filter(StoryJob.job_id == job_id).first()

        if not job:
            return

        try:
            job.status = "processing"
            db.commit()

            story = StoryGenerator.generate_story(db, session_id, theme)

            job.story_id = story.id  # todo: update story id
            job.status = "completed"
            job.completed_at = datetime.now()
            db.commit()
        except Exception as e:
            job.status = "failed"
            job.completed_at = datetime.now()
            job.error = str(e)
            db.commit()
    finally: #close database instance
        db.close()

#GET FULL STORY DATA
# Retrieves story by id.

# If not found, returns 404.

# Calls build_complete_story_tree to build the entire story tree response.
@router.get("/{story_id}/complete", response_model=CompleteStoryResponse)
def get_complete_story(story_id: int, db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code = 404, detail="Story Not Found")
    
    complete_story = build_complete_story_tree(db, story)
    return complete_story

#HELPER
def build_complete_story_tree(db: Session, story: Story) -> CompleteStoryResponse:
    nodes = db.query(StoryNode).filter(StoryNode.story_id == story.id).all()
    
    node_dict = {}
    for node in nodes:
        node_response = CompleteStoryNodeResponse(
            id=node.id,
            content=node.content,
            is_ending=node.is_ending,
            is_winning_ending=node.is_winning_ending, 
            options=node.options
        )

        node_dict[node.id] = node_response
    root_node = next((node for node in nodes if node.is_root), None)
    if not root_node:
        raise HTTPException(status_code=500, detail="Story root node not found")
    return CompleteStoryResponse(
        id=story.id,
        title=story.title,
        session_id=story.session_id,
        created_at=story.created_at,
        root_node=node_dict[root_node.id],
        all_nodes=node_dict
    )
#Queries all nodes belonging to the story.

# Builds a dictionary mapping node IDs to serialized node data.

# Finds the root node (start of the story).

# Returns a complete story response including all nodes and root node.


