#models.py
#Pydantic data models, defines the shape of our AI story data

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

#each option in the story has text and points to another node
class StoryOptionLLM(BaseModel):
    text: str = Field(description= "the text of the option shown to the user")
    nextNode: dict[str, Any] = Field(description= "the next node content and its options")

#A node in the story — contains text, ending info, and possible choices
class StoryNodeLLM(BaseModel):
    content: str = Field(description="The main content of the story node")
    isEnding: bool = Field(description="Whether this node is an ending node")
    isWinningEnding: bool = Field(description="Whether this node is a wninning ending node")
    options: Optional[List[StoryOptionLLM]] = Field(default=None, description="The options for this node")

#The full story structure returned by the AI
class StoryLLMResponse(BaseModel):
    title: str = Field(description="The title of the story")
    rootNode: StoryNodeLLM = Field(description="The root node of the story")