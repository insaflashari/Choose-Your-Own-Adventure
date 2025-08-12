#story.py
#These represent the actual story content and its nodes in your database.

##similar to binary tree structure
# story name
# theme
# first_option
# children: [go_left, go_right]
    # text
    # options: []

#sqlalchemy is known as a ORM (Object Relational Mapping), allow us to map data 
# into pythn code, so we dont write sql code (structured-query language)
#typically how u interact with the database
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.sql import func #functions
from sqlalchemy.orm import relationship #make relationship

from db.database import Base

#Represents the whole story.
# Has a title, linked to a user session.
# Tracks when the story was created.
# The nodes attribute sets up a relationship to StoryNode — so you can
# get all the story’s nodes easily

class Story(Base):
    __tablename__ = "stories"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    session_id = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    nodes = relationship("StoryNode", back_populates="story")

class StoryNode(Base):
    __tablename__ = "story_nodes"

    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id"), index=True) # Foreign key linking to Story
    content = Column(String)                                         # Text content of this node
    is_root = Column(Boolean, default=False)                         # True if this is the root node
    is_ending = Column(Boolean, default=False)                       # True if this node ends the story
    is_winning_ending = Column(Boolean, default=False)               # True if this node is a winning ending
    options = Column(JSON, default=list)                             # List of options from this node
    
    story = relationship(Story, back_populates="nodes")              # Link back to Story

# Each node belongs to one story (story_id foreign key).
# Contains the text content for this part of the story.
# Flags to mark if it’s the start of the story, an ending, or a winning ending.
# options is a JSON column — stores the choices for the player, e.g.,
# [
#   {"text": "Go left", "node_id": 5},
#   {"text": "Go right", "node_id": 6}
# ]
# Sets up a back-reference to the Story it belongs to.

# How these relate to your story_generator.py logic
# When GPT generates a story, it’s saved as a Story row.
# Each branching piece of the story is saved as a StoryNode linked to that story.
# The options field stores player choices and links to other nodes by their IDs, making a tree/graph structure.
# The StoryJob model tracks the process of generating the story — when it started, ended, or failed.

