#story.py
##This file defines schemas related to story nodes and stories themselves.
from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel

#Defines a story option that the user can pick.
# text is the option text shown to the user.
# node_id optionally links to the next node in the story tree.
class StoryOptionsSchema(BaseModel):
    text: str
    node_id: Optional[int] = None

#Base story node model with:
# content — text describing this node.
# is_ending — whether this node is an ending node.
# is_winning_ending — whether this node is a winning ending.
class StoryNodeBase(BaseModel):
    content: str
    is_ending: bool=False
    is_winning_ending: bool=False

#Extends StoryNodeBase.

# Adds:
    # id — node’s unique database id.
    # options — list of options available at this node.
# Used for returning node data with all necessary info.

# from_attributes=True enables reading from ORM models.
class CompleteStoryNodeResponse(StoryNodeBase):
    id: int
    options: List[StoryOptionsSchema] = []

    class Config:
        from_attributes = True

#Base story info with:

# title — story title.
# session_id — optional session id of the user who owns this story.
class StoryBase(BaseModel):
    title: str
    session_id: Optional[str] = None

    class Config:
        from_attributes = True

#Input model for creating a new story.
# Only requires a theme string.
class CreateStoryRequest(BaseModel):
    theme: str

# Extends StoryBase.

# Used to return a full story with all nodes.

# Adds:

# id — story id.

# created_at — timestamp.

# root_node — the root story node (start).

# all_nodes — dictionary mapping node IDs to node data for all nodes in the story.
class CompleteStoryResponse(StoryBase):
    id: int
    created_at: datetime
    root_node: CompleteStoryNodeResponse
    all_nodes: Dict[int, CompleteStoryNodeResponse]

    class Config:
        from_attributes = True

    

    
